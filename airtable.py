from functools import wraps
from fastapi import Request, UploadFile
from starlette.responses import Response
import asyncio
import requests
import json
import os

import json

def is_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False

def log_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Build request_data object with action and request details, including thread_id if present
        # Serialize request_data, handling UploadFile objects and other parameters
        def serialize_request_data(data):
            print(f"RECURSIVE INPUT into serialize_request_data  {data}")
            print(f"INPUT type {type(data)}")
            if isinstance(data, UploadFile):
                print(f"is UPloadFile fastapi  {data}")
                # Extract the file information without reading the content, which is not serializable
                return {
                    "filename": data.filename,
                    "content_type": data.content_type,
                    "size": data.file_size,  # Renamed from file_size to size for consistency
                    "file": None  # We cannot serialize the file content, so we set it to None
                }
            if isinstance(data, dict):
                return {k: serialize_request_data(v) for k, v in data.items() if not isinstance(v, UploadFile)}
            elif isinstance(data, list):
                return [serialize_request_data(item) for item in data]
            else:
                return data

        request_data = {
            "action": func.__name__,
            "request": serialize_request_data({'args': args, **kwargs})  # Serialize both args and kwargs
        }
        print(f"Logging input parameters for action '{func.__name__}': {request_data}")

        # Serialize request_data, handling UploadFile objects and other parameters
        # def serialize_request_data(data):
        #     if isinstance(data, dict):
        #         return {k: serialize_request_data(v) for k, v in data.items()}
        #     elif isinstance(data, list):
        #         return [serialize_request_data(item) for item in data]
        #     elif isinstance(data, UploadFile):
        #         # Extract the file information without reading the content, which is not serializable
        #         return {
        #             "filename": data.filename,
        #             "content_type": data.content_type,
        #             "size": data.file_size,  # Renamed from file_size to size for consistency
        #             "file": None  # We cannot serialize the file content, so we set it to None
        #         }
        #     else:
        #         return data

        # request_data_serializable = serialize_request_data(request_data)

        # Call the actual endpoint function
        response = await func(*args, **kwargs)

        # Build response_data object
        response_data = {
            "status_code": response.status_code if isinstance(response, Response) else "N/A",
            "body": response.body.decode("utf-8") if isinstance(response, Response) and hasattr(response, "body") else str(response)
        }
        print(f"Logging Response: {response_data}")

        # Pass thread_id and message to log_to_airtable if they exist in request_data
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
                "Thread ID": thread_id if thread_id else "N/A",
                "Message": request_data_serializable.get('message', "N/A"),  # Retrieve the message from request_data_serializable
                "Action": request_data_serializable.get('action'),  # Include the Action field from request_data_serializable
                "Time": current_time  # Include the current time
            }
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"An error occurred while logging to Airtable: {e}")

