# This is a template and should be modified according to your application's needs.

from config import settings
from prompts import assistants

# Add thread to DB with platform identifier
def add_thread(thread_id: str, platform: str) -> None:
    """
    Adds a new thread to the database with the given thread ID and platform.

    Parameters:
    thread_id: The unique identifier for the thread.
    platform: The name of the platform where the thread originated.
    """
    url = "https://api.airtable.com/v0/app9KJE69rZ0WLnpV/Threads" # replace this with your Airtable Web API URL
    headers = {
        "Authorization": settings.airtable_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Thread ID": thread_id,
                "Platform": platform
            }
        }]
    }

    try:
        print(f"An error occurred while adding the thread: {e}")
    except Exception as e:
        # Handle exceptions like network errors, request timeouts, etc.
        print(f"An error occurred while adding the thread: {e}")

import json

def get_services(assistant_name: str) -> str:
    """
    Retrieves all available services that an assistant has through other assistants and returns them as a JSON string.

    Parameters:
    assistant_name: The name of the assistant for which to retrieve services.

    Returns:
    A JSON string representing a list of dictionaries, each containing the assistant name and description.
    """
    services = [
        {
            "assistant_name": name,
            "assistant_description": assistant.get("prompt")
        }
        for name, assistant in assistants.items()
    ]
    # Log the input parameter
    print(f"get_services called with assistant_name: {assistant_name}")
    return services
