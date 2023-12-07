from functools import wraps
from fastapi import Request
from starlette.responses import Response
import asyncio
import requests
import json
import os

def log_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Build request_data object with action and request details, including thread_id if present
        request_data = {
            "action": func.__name__,
            "request": {
                "args": args,
                "kwargs": kwargs
            }
        }
        # Check if 'thread_id' is a parameter and add it to request_data if present
        if 'thread_id' in kwargs:
            request_data['thread_id'] = kwargs['thread_id']
        print(f"Logging input parameters for action '{func.__name__}': {request_data}")

        # Call the actual endpoint function
        response = await func(*args, **kwargs)

        # Build response_data object
        response_data = {
            "status_code": response.status_code if isinstance(response, Response) else "N/A",
            "body": response.body.decode("utf-8") if isinstance(response, Response) and hasattr(response, "body") else str(response)
        }
        print(f"Logging Response: {response_data}")

        # Pass thread_id to log_to_airtable if it exists in request_data
        asyncio.create_task(log_to_airtable(request_data, response_data))

        return response
    return wrapper

AIRTABLE_BASE_ID = "your_airtable_base_id"
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY'] 

async def log_to_airtable(request_data, response_data):
    thread_id = request_data.get('thread_id', "N/A")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/log"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Request": json.dumps(request_data),
                "Response": json.dumps(response_data),
                "Thread ID": thread_id if thread_id else "N/A"
            }
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"An error occurred while logging to Airtable: {e}")

