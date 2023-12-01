# This is a template and should be modified according to your application's needs.

from config import settings


def custom_response_formatter(response):
    """
    Formats the response from the OpenAI assistant in a custom way.
    """
    # Implement your formatting logic here
    return formatted_response

def data_preprocessor(input_data):
    """
    Preprocesses input data before sending it to the OpenAI assistant.
    """
    # Implement your preprocessing logic here
    return processed_data


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
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("Thread added to DB successfully.")
        else:
        # Handle non-200 HTTP response status codes
            print(
                f"Failed to add thread: HTTP Status Code {response.status_code}, Response: {response.text}"
            )
    except Exception as e:
        # Handle exceptions like network errors, request timeouts, etc.
        print(f"An error occurred while adding the thread: {e}")

