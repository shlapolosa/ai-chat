import asyncio
import time
from openai_assistant_manager import OpenAIAssistantManager

class ChatService:
    def __init__(self, assistant_manager):
        self._assistant_manager = assistant_manager

    # def get_loaded_assistants_info(self) -> List[dict]:
    #     # This method will encapsulate the assistant_manager and return the necessary info
    #     # without exposing the OpenAIAssistantManager or its components.
    #     return [
    #         {
    #             "assistant_name": assistant.get("assistant_name"),
    #             "assistant_id": assistant.get("assistant_id")
    #         }
    #         for assistant in self._assistant_manager.all_assistants_info
    #     ]

    async def start_thread(self, platform: str):
        assistant_id = self.assistant_manager.get_assistant_id_by_platform(platform)
        thread_id = self.assistant_manager.create_thread(assistant_id=assistant_id)
        return thread_id

    async def handle_chat(self, action: str, thread_id: str, user_input: str):
        assistant_id = self.assistant_manager.get_assistant_id_by_action(action)
        run_id = self.assistant_manager.send_message(thread_id, assistant_id, user_input)
        return run_id

    async def check_run_status(self, thread_id: str, run_id: str):
        start_time = time.time()
        while time.time() - start_time < 8:
            status = self.assistant_manager.check_run_status(thread_id, run_id)
            if status == 'completed':
                # Assuming there's a method to fetch and clean the message
                message_content = self._fetch_and_clean_message(thread_id)
                return message_content, 'completed'
            await asyncio.sleep(1)
        return "timeout", 'timeout'

    def _fetch_and_clean_message(self, thread_id):
        # Fetch the message and clean it up as required
        return "Cleaned message content"  # Placeholder
