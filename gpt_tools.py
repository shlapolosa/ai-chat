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


def get_authorisation_url(amount):
    """
    Get authorisation link for confirming payment.

    Parameters:
    amount: How much should be paid

    Returns:
    The url for me to authorise the payment.
    """

    from nedbank_api import write_cache
    import decimal
    from nedbank_api import token_light, create_payment_intent
    bearer_token = token_light("payments")
    amount = decimal.Decimal('53.6')
    consent_id, redirect_url = create_payment_intent(bearer_token, amount)
    write_cache('payment_amount', str(amount))
    write_cache('payment_consent_id', consent_id)
    return redirect_url

import requests

def schedule_event(schedule_date: str, schedule_event_type: str, instruction: str, thread_id: str, run_id: str) -> None:
    """
    Schedules an event to be processed at a later period.

    Parameters:
    schedule_date: The date when the event is scheduled.
    schedule_event_type: The type of the scheduled event. the type can either be TRANSACTION, REMINDER, ALERT, INFORMATIONAL 
    instruction: Instructions for the scheduled event with a clear prompt of what needs to happen, by whom, with reference to what and any meaning details that will aid the process.
    thread_id: The thread ID associated with the event as derived from the context that created the event.
    run_id: The run ID associated with the event as derived from the cntext that created the event.
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
                "Instruction": instruction,
                "Thread ID": thread_id,
                "Run ID": run_id
            }
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        print(f"Event scheduled successfully: {data}")
    except Exception as e:
        print(f"An error occurred while scheduling the event: {e}")
