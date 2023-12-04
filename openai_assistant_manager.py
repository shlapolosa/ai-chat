import asyncio
import inspect
import json
import logging
import openai
import os
from typing import Any, Dict, List, get_type_hints

import gpt_tools
import prompts

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIAssistantManager:
#TODO: Socrates to split file into OpenAIAssistManager and APIRequestHandler files

    def __init__(self, openai_api_key):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.api_version = 'v1'  # Assuming the API version is v1, adjust as necessary
        self.organization = 'your_organization'  # Replace with actual organization name
        self.all_assistants_info = self.load_or_create_assistants()

    @property
    def client_details(self):
        return {
            "organization": self.organization,
            "api_version": self.api_version
        }

    def upload_file(self, file: str, purpose: str = "assistants") -> str:
        """
        Uploads a file to OpenAI and returns the file ID.

        Parameters:
        file: The path to the file to be uploaded.
        purpose: The purpose of the file upload, defaults to "assistants".

        Returns:
        The file ID from OpenAI after the upload.
        """
        with open(file, "rb") as file_data:
            response = openai.File.create(file=file_data, purpose=purpose)
        return response.id
    

    def update_assistant_id_in_prompts(self, assistant_name, assistant_id):
        # Read the content of the prompts.py file
        with open('prompts.py', 'r') as file:
            lines = file.readlines()
        
        # Modify the assistant_id for the specific assistant
        for i, line in enumerate(lines):
            if f'"{assistant_name}": ' in line:
                for j in range(i+1, len(lines)):
                    if '"assistant_id":' in lines[j]:
                        lines[j] = f'        "assistant_id": "{assistant_id}",\n'
                        break
                break
        
        # Write the updated content back to the prompts.py file
        with open('prompts.py', 'w') as file:
            file.writelines(lines)

            
    def load_or_create_assistants(self):
        logger.info("Creating all assistants based on the configuration...")
        all_assistants_info = []
        for assistant_name, config in prompts.assistants.items():
            logger.info(f"Assistant {assistant_name} created with config: {config}")
            if config.get("active", True):
                if config.get("assistant_id"):
                    logger.info(f"Loading assistant: {assistant_name}")
                    assistant_info = {
                        "assistant_name": assistant_name,
                        "assistant_id": config.get("assistant_id")
                    }
                    all_assistants_info.append(assistant_info)
                else:
                    logger.info(f"Creating assistant: {assistant_name}")
                    assistant_creation_params = {
                        "name": assistant_name,
                        "model": "gpt-4-1106-preview",
                        "instructions": config.get("prompt"),
                        "tools": self.generate_tool_configurations(config.get("tools", [])),
                        "file_ids": self.upload_knowledge_files(config.get("knowledge_files", []))
                    }
                    logger.info(f"Creating assistant with parameters: {assistant_creation_params}")
                    assistant = self.client.beta.assistants.create(**assistant_creation_params)
                    # Store the assistant information
                    assistant_info = {
                        "assistant_name": assistant_name,
                        "assistant_id": assistant.id
                    }
                    all_assistants_info.append(assistant_info)
                    # Update the assistant_id in the prompts.py file
                    self.update_assistant_id_in_prompts(assistant_name, assistant.id)
                    logger.info(f"Assistant {assistant_name} created with ID: {assistant.id}")
            else:
                logger.info(f"Skipping inactive assistant: {assistant_name}")
        logger.info("All assistants have been created.")
        return all_assistants_info


    def generate_tool_configurations(self, tools: List[Dict]) -> List[Dict]:
        tools_config = []
        for tool in tools:
            if tool["type"] == "function" and hasattr(gpt_tools, tool["name"]):
                function_tool = getattr(gpt_tools, tool["name"])
                signature = inspect.signature(function_tool)
                type_hints = get_type_hints(function_tool)
                docstring = inspect.getdoc(function_tool)
                description_lines = docstring.split("\n")
                function_description = description_lines[0]
                properties = {}
                for param_name, param in signature.parameters.items():
                    # Determine the JSON schema type based on the Python type hint
                    python_type = type_hints.get(param_name)
                    json_schema_type = 'string'  # Default to string for unrecognized types
                    if python_type == str:
                        json_schema_type = 'string'
                    elif python_type == int:
                        json_schema_type = 'integer'
                    elif python_type == bool:
                        json_schema_type = 'boolean'
                    # Add more type mappings as needed
                    param_description = next((line for line in description_lines if line.startswith(param_name + ":")), "").split(": ")[1]
                    properties[param_name] = {
                        "type": json_schema_type,
                        "description": param_description
                    }
                function_tool_config = {
                    "type": "function",
                    "function": {
                        "name": function_tool.__name__,
                        "description": function_description,
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": list(signature.parameters.keys())
                        }
                    }
                }
                tools_config.append(function_tool_config)
            else:
                tools_config.append({"type": tool["type"]})
        return tools_config


    def upload_knowledge_files(self, filenames):
        logger.info("Uploading knowledge files...")
        file_ids = []
        for filename in filenames:
            if filename:
                logger.info(f"Uploading file: {filename}")
                with open(filename, "rb") as file:
                    uploaded_file = self.client.files.create(file=file, purpose='assistants')
                    file_ids.append(uploaded_file.id)
                    logger.info(f"File uploaded with ID: {uploaded_file.id}")
        logger.info("All knowledge files have been uploaded.")
        return file_ids

    def create_thread(self):
        thread = self.client.beta.threads.create()
        return thread.id

    def send_message(self, thread_id, assistant_id, message, file=None):
        file_ids = []
        if file:
            file_id = self.upload_file(file)
            file_ids.append(file_id)
        # Include the file_ids in the message payload if any file was uploaded
        logger.info(f"send_message: Sending message to thread_id={thread_id}, assistant_id={assistant_id}, with file_ids={file_ids}")
        message_creation_data = {
            "thread_id": thread_id,
            "role": "user",
            "content": message
        }
        if file_ids:
            message_creation_data["file_ids"] = file_ids
        self.client.beta.threads.messages.create(**message_creation_data)
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        logger.info(f"send_message: Message sent with run_id={run.id}")
        return run.id

    async def check_run_status(self, thread_id, run_id):
        run_status = self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        logger.info(f"check_run_status: Current run status response={run_status.status}")
        if run_status.status == 'requires_action':
            logger.info("Action required for the run. Processing...")
            assistant_id = run_status.assistant_id
            logger.info(f"Assistant ID for action: {assistant_id}")
            # Find the corresponding assistant configuration
            assistant_config = next((config for config in prompts.assistants.values() if config.get("assistant_id") == assistant_id), None)
            if assistant_config:
                logger.info(f"Found assistant configuration for assistant ID {assistant_id}")
                # Handle the function call
                for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                    function_name = tool_call.function.name
                    logger.info(f"Processing tool call for function: {function_name} and assistant_config: {assistant_config.get('tools', [])}")
                    logger.info(f"The check for function name returns: {function_name in assistant_config.get('tools', [])}")
                    
                    tool_found = any(tool.get("name") == function_name for tool in assistant_config.get("tools", []))
                    if tool_found:
                        # Process the function call
                        function_tool = getattr(gpt_tools, function_name, None)
                        logger.info(f"Function toot: {function_tool}")
                        if function_tool:
                            logger.info(f"Found function tool: {function_name}")
                            arguments = json.loads(tool_call.function.arguments)
                            logger.info(f"Function arguments: {arguments}")
                            if function_tool:
                                if asyncio.iscoroutinefunction(function_tool):
                                    output = await function_tool(**arguments)
                                else:
                                    output = function_tool(**arguments)
                                logger.info(f"Function output: {output}")
                                self.client.beta.threads.runs.submit_tool_outputs(
                                    thread_id=thread_id,
                                    run_id=run_id,
                                    tool_outputs=[{
                                        "tool_call_id": tool_call.id,
                                        "output": json.dumps(output)
                                    }]
                                )
                                logger.info(f"Submitted tool outputs for tool call ID: {tool_call.id}")
            await asyncio.sleep(1)  # Sleep to avoid rapid API calls
            logger.info("Completed action processing and sleeping for 1 second.")
        return run_status.status

    def get_assistant_id_by_name(self, assistant_name: str = None) -> str:
        """
        Retrieves the assistant ID for the given assistant name.
        If the assistant name is empty or None, returns the default assistant ID.

        Parameters:
        assistant_name: The name of the assistant to retrieve the ID for.

        Returns:
        The assistant ID corresponding to the assistant name, or the default assistant ID if not specified.
        """
        if not assistant_name:
            # Find and return the default assistant ID
            for assistant in self.all_assistants_info:
                if assistant.get("default", True):
                    return assistant["assistant_id"]
            # If no default is set, return None or raise an error as appropriate
            return None

        # Find and return the assistant ID for the given name
        for assistant in self.all_assistants_info:
            if assistant["assistant_name"] == assistant_name:
                return assistant["assistant_id"]

        # If the assistant name does not exist, return None or raise an error as appropriate
        return None
