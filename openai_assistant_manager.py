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
                        "tools": [self.generate_tool_configurations(getattr(gpt_tools, tool["function"])) for tool in config.get("tools", []) if "type" in tool and tool["type"] == "function" and hasattr(gpt_tools, tool["function"])],
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


    def generate_tool_configurations(self, function_tool: Any) -> List[Dict]:
        tools_config = [{"type": "retrieval"}]
        signature = inspect.signature(function_tool)
        type_hints = get_type_hints(function_tool)
        docstring = inspect.getdoc(function_tool)
        description_lines = docstring.split("\n")
        function_description = description_lines[0]
        properties = {}
        for param_name, param in signature.parameters.items():
            param_description = next((line.split(": ")[1] for line in description_lines if line.startswith(param_name)), "")
            properties[param_name] = {
                "type": type_hints[param_name].__name__ if param_name in type_hints else "string",
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

    def create_thread(self, assistant_id):
        thread = self.client.beta.threads.create(assistant_id=assistant_id)
        return thread.id

    def send_message(self, thread_id, assistant_id, message):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        return run.id

    def check_run_status(self, thread_id, run_id):
        run_status = self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return run_status.status

    def get_assistant_id_by_action(self, action):
        # Example implementation; adjust based on your action-to-assistant mapping
        action_to_assistant_map = {
            "finance": "financial_assistant",
            "general": "general_assistant",
            # Add other mappings as needed
        }
        assistant_name = action_to_assistant_map.get(action, "default_assistant")
        for assistant in self.assistants_info:
            if assistant["assistant_name"] == assistant_name:
                return assistant["assistant_id"]
        return None
