from functools import wraps
from fastapi import Request
from starlette.responses import Response
import requests
import json
import os

def log_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the request object from the arguments
        request = None
        if 'request' in kwargs:
            request = kwargs['request']
        elif args and isinstance(args[0], Request):
            request = args[0]
        
        # Perform logging of the request here
        if request:
            print(f"Logging Request: {request.method} {request.url}")
        else:
            print("Logging Request: Request object not found")

        # Call the actual endpoint function
        response = await func(*args, **kwargs)

        # Perform logging of the response here
        if isinstance(response, Response):
            print(f"Logging Response: {response.status_code}")
        else:
            print(f"Logging Response: Custom Response or Response object not found")

        return response
    return wrapper

AIRTABLE_BASE_ID = "your_airtable_base_id"
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY'] 

async def log_to_airtable(request_data, response_data):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Requests"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Request": json.dumps(request_data),
                "Response": json.dumps(response_data)
            }
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"An error occurred while logging to Airtable: {e}")


def airtable_logger(func):
    print(f"inside logger function")
    async def wrapper(*args, **kwargs):
        # Extracting FastAPI request and response
        print(f"inside wraaper")
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        response = await func(*args, **kwargs)
        print(f"got response")
        if request:
            request_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": str(request.headers),
                "body": (await request.body()).decode("utf-8")
            }
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.body.decode("utf-8") if hasattr(response, "body") else "Response body not available"
            }
            # log_to_airtable(request_data, response_data)
            print(f"logging request: {request_data} with response: {response_data}")

        return response

    return wrapper
