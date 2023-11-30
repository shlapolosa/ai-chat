import json
import os
from openai import OpenAI_Client
import prompts
import gpt_tools

import json
import os
from openai import OpenAI_Client
import prompts
import gpt_tools

class OpenAIAssistantManager:
    def __init__(self, openai_api_key):
        self._client = OpenAI_Client(openai_api_key)
        self.assistants_info = self.load_or_create_assistants()
        self.api_version = 'v1'  # Assuming the API version is v1, adjust as necessary
        self.organization = 'your_organization'  # Replace with actual organization name

    @property
    def client_details(self):
        return {
            "organization": self.organization,
            "api_version": self.api_version
        }

    def load_or_create_assistants(self):
        assistants_info_path = "assistants_info.json"
        if os.path.exists(assistants_info_path):
            with open(assistants_info_path, "r") as file:
                return json.load(file)
        else:
            all_assistants_info = self.create_all_assistants()
            with open(assistants_info_path, "w") as file:
                json.dump(all_assistants_info, file, indent=4)
            return all_assistants_info

    def create_all_assistants(self):
        all_assistants_info = []
        for assistant_name, config in prompts.assistants.items():
            if config.get("active", False):
                tool_function_names = config.get("tools", "").split(", ")
                tools = [getattr(gpt_tools, name) for name in tool_function_names if hasattr(gpt_tools, name)]

                file_ids = self.upload_knowledge_files(config.get("knowledge", "").split(", "))

                assistant = self._client.beta.assistants.create(
                    instructions=config.get("prompt"),
                    model="gpt-4-1106-preview",
                    tools=tools,
                    file_ids=file_ids
                )
                assistant_info = {
                    "assistant_name": assistant_name,
                    "assistant_id": assistant.id
                }
                all_assistants_info.append(assistant_info)
        return all_assistants_info

    def upload_knowledge_files(self, filenames):
        file_ids = []
        for filename in filenames:
            if filename:
                with open(filename, "rb") as file:
                    uploaded_file = self._client.files.create(file=file, purpose='answers')
                    file_ids.append(uploaded_file.id)
        return file_ids

    def create_thread(self, assistant_id):
        thread = self._client.beta.threads.create(assistant_id=assistant_id)
        return thread.id

    def send_message(self, thread_id, assistant_id, message):
        self._client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        run = self._client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        return run.id

    def check_run_status(self, thread_id, run_id):
        run_status = self._client.beta.threads.runs.retrieve(
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

    def get_assistant_id_by_platform(self, platform):
        # Similar to get_assistant_id_by_action, map platform to assistant
        return None
