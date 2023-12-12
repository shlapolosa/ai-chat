import json
import time

import requests
import textwrap

import urllib3
from IPython.lib.pretty import pprint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}
response = requests.put('http://localhost:8000/api/v2/chat', headers=headers, verify=False)
thread_id = response.json().get('thread_id')


def send_message(message):
    payload = {
        "thread_id": thread_id,
        "message": message
    }
    response = requests.post(
        'http://localhost:8000/api/v2/chat',
        headers=headers,
        data=json.dumps(payload),
        verify=False
    )
    run_id = response.json().get('run_id')

    message = 'Run Stopped'
    while message == 'Run Stopped':
        response = requests.get(f'http://localhost:8000/api/v2/chat?thread_id={thread_id}&run_id={run_id}',
                                headers=headers,
                                verify=False)
        message = response.json().get('message')
        time.sleep(3)


    # try:
    #     message = textwrap.fill(message, 60)
    #     a, b = message.split('(')
    #     b = b.replace(r'\n', '')
    #     message = f"{a}{b}"
    #     print(message)
    # except:
    # print(textwrap.fill(message, 60))
    print(message)
    return message


# return(response.json())
