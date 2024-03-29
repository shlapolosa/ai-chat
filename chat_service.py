import asyncio
import time
from typing import List
from fastapi import UploadFile
from openai_assistant_manager import OpenAIAssistantManager

class ChatService:
    def __init__(self, assistant_manager):
        self._assistant_manager = assistant_manager

    def get_loaded_assistants_info(self) -> List[dict]:
        # This method will encapsulate the assistant_manager and return the necessary info
        # without exposing the OpenAIAssistantManager or its components.
        return [
            {
                "assistant_name": assistant.get("assistant_name"),
                "assistant_id": assistant.get("assistant_id")
            }
            for assistant in self._assistant_manager.all_assistants_info
        ]

    async def start_thread(self, assistant_name: str = None):
        thread_id = self._assistant_manager.create_thread()
        return thread_id

    async def handle_chat(self, assistant_name: str, thread_id: str, user_input: str, file: UploadFile = None):
        assistant_id = self._assistant_manager.get_assistant_id_by_name(assistant_name)
        if file:
            # Here you can add logic to handle the file, e.g., save it or process it.
            print(f"chat_service: found the file{file.filename}")
            pass  # Placeholder for file handling logic
        run_id = await self._assistant_manager.send_message(thread_id, assistant_id, user_input, file)
        return run_id

    async def check_run_status(self, thread_id: str, run_id: str):
        start_time = time.time()
        while time.time() - start_time < 8:
            status = await self._assistant_manager.check_run_status(thread_id, run_id)
            if status in ['completed', 'expired', 'cancelled', 'failed']:
                message_content = "Run Stopped" if status != 'completed' else self._fetch_and_clean_message(thread_id)
                return message_content, status
            await asyncio.sleep(1)
        return "Run Stopped", 'timeout'

    def _fetch_and_clean_message(self, thread_id):
        # Fetch the latest message
        messages = self._assistant_manager.client.beta.threads.messages.list(thread_id=thread_id)
        # Extracting the 'value' from the 'text' attribute of the first item in the list
        message_content = messages.data[0].content[0].text.value
        print(f"Message content before cleaning: {message_content}")
        return message_content
