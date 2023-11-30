from openai import OpenAI_Client
from assistant_creator import AssistantCreator
from thread_manager import ThreadManager
from assistant_config_loader import AssistantConfigLoader
from assistant_mapper import AssistantMapper
import prompts  # Assuming this is a module with assistant configurations

class OpenAIAssistantManager:
    def __init__(self, openai_api_key):
        self.client = OpenAI_Client(openai_api_key)
        self.config_loader = AssistantConfigLoader("assistants_info.json")
        self.assistants_info = self.config_loader.load_or_create_assistants()
        self.creator = AssistantCreator(self.client)
        self.thread_manager = ThreadManager(self.client)
        self.mapper = AssistantMapper(self.assistants_info)

    def create_all_assistants(self):
        configurations = prompts.assistants  # Assuming this is defined in prompts.py
        self.assistants_info = self.creator.create_all_assistants(configurations)
        # Save the updated assistants info back to the file if necessary

    def create_thread(self, platform):
        assistant_id = self.mapper.get_assistant_id_by_platform(platform)
        return self.thread_manager.create_thread(assistant_id)

    def send_message(self, action, thread_id, user_input):
        assistant_id = self.mapper.get_assistant_id_by_action(action)
        return self.thread_manager.send_message(thread_id, assistant_id, user_input)

    def check_run_status(self, thread_id, run_id):
        return self.thread_manager.check_run_status(thread_id, run_id)

    def fetch_message(self, thread_id):
        # Placeholder for a method to fetch a message from a thread
        # The actual implementation depends on how you manage chat histories
        return "Message content"

    # Additional methods as needed...
