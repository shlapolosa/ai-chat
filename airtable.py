from functools import wraps
from fastapi import Request, UploadFile
from starlette.responses import Response
import asyncio
import requests
import json
import os
import re

import json

def is_not_serializable(obj):
    try:
        json.dumps(obj)
        return False
    except (TypeError, OverflowError):
        return True

def log_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Build request_data object with action and request details, including thread_id if present
        # Serialize request_data, handling UploadFile objects and other parameters
        def serialize_request_data(data):
            if isinstance(data, dict):
                serialized_data = {}
                for k, v in data.items():
                    if k == 'file':
                        # Create a serialized file object
                        serialized_data['file'] = {
                            "filename": v.filename,
                            "content_type": v.content_type,
                            "size": v.size,  # Renamed from file_size to size for consistency
                            "type": "file"  # We cannot serialize the file content, so we set it to None
                        }
                    else:
                        serialized_data[k] = serialize_request_data(v)
                return serialized_data
            elif isinstance(data, list):
                return [serialize_request_data(item) for item in data]
            else:
                return data

        request_data = {
            "action": func.__name__,
            "request": serialize_request_data({'args': args, **kwargs})  # Serialize both args and kwargs
        }
        print(f"Logging input parameters for action '{func.__name__}': {request_data}")


        # Call the actual endpoint function
        response = await func(*args, **kwargs)

        # Build response_data object
        response_data = {
            "status_code": response.status_code if isinstance(response, Response) else "N/A",
            "body": response.body.decode("utf-8") if isinstance(response, Response) and hasattr(response, "body") else str(response)
        }
        print(f"Logging Response: {response_data}")

        # Pass thread_id and message to log_to_airtable if they exist in request_data in an async way, dont wait for response
        asyncio.create_task(log_to_airtable(request_data, response_data))

        return response
    return wrapper

async def log_to_airtable(request_data_serializable, response_data):
    
    AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']
    AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY'] 

    from datetime import datetime
    print(f"log_to_airtable request_data: {request_data_serializable}")
    thread_id = request_data_serializable.get('thread_id', "N/A")
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/log"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Request": json.dumps(request_data_serializable),
                "Response": json.dumps(response_data),
                "Thread ID": request_data_serializable.get('request', {}).get('thread_id', "N/A"),
                "Run ID": request_data_serializable.get('request', {}).get('run_id', "N/A"),
                "Request Message": request_data_serializable.get('request', {}).get('message', "N/A"),  # Retrieve the message from request_data_serializable
                "Action": request_data_serializable.get('action'),  # Include the Action field from request_data_serializable
                "Response Message": (match.group(1) or match.group(2) if (match := re.search(r'message=(?:\'([^\']*)\'|"([^"]*)")', response_data.get('body'))) else response_data.get('body', {}).get('message', "N/A")) if isinstance(response_data.get('body'), str) else "N/A",
                "Time": current_time  # Include the current time
            }
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"An error occurred while logging to Airtable: {e}")

