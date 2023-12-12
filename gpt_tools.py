# This is a template and should be modified according to your application's needs.

from config import settings
from prompts import assistants
import os

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


# Add thread to DB with platform identifier
def book_job(location: str, user_id: str) -> str:
    """
    Book a job or service for a user and returns a reference

    Parameters:
    location: The users location address.
    user_id: The user's identity number.
    """
    # url = "https://api.airtable.com/v0/app9KJE69rZ0WLnpV/Threads" # replace this with your Airtable Web API URL
    # headers = {
    #     "Authorization": settings.airtable_api_key,
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "records": [{
    #         "fields": {
    #             "Thread ID": thread_id,
    #             "Platform": platform
    #         }
    #     }]

    # }

    try:
        print(f"booking job")
        return "xyz123"
    except Exception as e:
        # Handle exceptions like network errors, request timeouts, etc.
        print(f"failed to book job: {e}")


def get_jobs_for_user(user_id: str) -> str:
    """
    get all the previously booked jobs for this user as a list of references to those jobs

    Parameters:
    user_id: The user's identity number.
    """
    # url = "https://api.airtable.com/v0/app9KJE69rZ0WLnpV/Threads" # replace this with your Airtable Web API URL
    # headers = {
    #     "Authorization": settings.airtable_api_key,
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "records": [{
    #         "fields": {
    #             "Thread ID": thread_id,
    #             "Platform": platform
    #         }
    #     }]

    # }

    try:
        print(f"getting jobs")
        return ["xyz123","wxyz324"]
    except Exception as e:
        # Handle exceptions like network errors, request timeouts, etc.
        print(f"failed to get jobs: {e}")


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


def make_payment(amount):
    """
    Get make a payment and authorisation link for confirming payment.

    Parameters:
    amount: How much should be paid

    Returns:
    The url for me to authorise the payment.
    """

    from nedbank_api import write_cache
    import decimal
    from nedbank_api import token_light, create_payment_intent
    bearer_token = token_light("payments")
    print(f"got light token: {bearer_token}")
    amount = decimal.Decimal(amount)
    consent_id, redirect_url = create_payment_intent(bearer_token, amount)
    print(f"created intent")
    write_cache('payment_amount', str(amount))
    write_cache('payment_consent_id', consent_id)
    return redirect_url

import requests

def schedule_event(schedule_date: str, schedule_event_type: str, instruction: str) -> dict:
    """
    Schedules an event to be processed at a later period and returns the response from the API.

    Parameters:
    schedule_date: The date when the event is scheduled.
    schedule_event_type: The type of the scheduled event. The type can either be TRANSACTION, REMINDER, ALERT, INFORMATIONAL.
    instruction: Instructions for the scheduled event with a clear prompt of what needs to happen, by whom, with reference to what and any meaningful details that will aid the process.

    Returns:
    A dictionary representing the JSON response from the API. This can be a success response with the created record or an error response.

    Example of a success response:
    {
        "records": [
            {
                "id": "rec1234567890",
                "fields": {
                    "Schedule Date": "2023-04-15",
                    "Event Type": "REMINDER",
                    "Instruction": "Remind user about upcoming payment",
                    "Thread ID": "thread_abcdef",
                    "Run ID": "run_123456"
                },
                "createdTime": "2023-04-01T12:00:00.000Z"
            }
        ]
    }

    Example of an error response:
    {
        "error": "An error occurred while scheduling the event: Invalid API key provided"
    }
    """
    AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']
    AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/scheduled_job"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Schedule Date": schedule_date,
                "Event Type": schedule_event_type,
                "Instruction": instruction
            }
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        print(f"Event scheduled successfully: {data}")
        return response.json()  # Return the response from the API
    except Exception as e:
        print(f"An error occurred while scheduling the event: {e}")
        return {"error": str(e)}  # Return the error as a dictionary
