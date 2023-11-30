import json
import os
from openai import OpenAI_Client
import prompts
import gpt_tools

class OpenAIAssistantManager:
    def __init__(self, openai_api_key):
        self._client = OpenAI_Client(openai_api_key)
        self.assistants_info = self.load_or_create_assistants()

    # ... (rest of the updated class definition) ...
