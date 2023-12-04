# FastAPI Chat Client Backend

## Overview
For a demo video of how it works go to: [watch the demo](https://capture.dropbox.com/0ViaHzrWQowe2de)F
This project is a backend for a chat client, built with FastAPI. It provides endpoints to handle chat requests, manage conversations, and integrate with external services like Sentry for error tracking.

## Requirements
- Python 3.7+
- Poetry for dependency management

## Setting Up the Environment
Before running the application, you need to set up the environment variables. Copy the `.env.example` file to a new file named `.env` and update the variables accordingly.

```bash
cp .env.example .env
# Edit .env with your settings
```

## Installation
To install the project dependencies, use Poetry:

```bash
poetry install
```

## Running the Application
To run the application, navigate to the project directory and use the following command:

```bash
poetry run uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000` by default.

You can also specify the host and port by adding `--host 0.0.0.0 --port 8080` to the command if you want the application to be accessible on a different IP and port.

## Updating Prompts and Tools
To update the prompts or the tools used by the assistants, you need to modify the `prompts.py` and `gpt_tools.py` files respectively.

For `prompts.py`, you can add or modify the assistant configurations within the `assistants` dictionary. Each assistant should have a unique name and can include properties such as `active`, `default`, `assistant_id`, `prompt`, `tools`, and `knowledge_files`.

For `gpt_tools.py`, you can add new functions or modify existing ones that are used as tools by the assistants. Ensure that each tool function has the appropriate parameters and return types as expected by the assistants.

## Environment Configuration
The application uses environment variables for configuration. These variables are loaded from the `.env` file at the root of the project directory. To update the environment variables, edit the `.env` file with the new values for keys such as `OPENAI_API_KEY`, `AIRTABLE_API_KEY`, `SENTRY_DSN`, `DATABASE_URL`, `ENVIRONMENT`, `BACKEND_CORS_ORIGINS`, and `PROJECT_NAME`.

After updating the `.env` file, restart the application for the changes to take effect.

## Environment Variables
The following environment variables are required for the project:

- `PROJECT_NAME`: The name of the project.
- `SENTRY_DSN`: The DSN for Sentry integration (optional).

These variables should be set in the `.env` file.

## Poetry Dependency Management
This project uses Poetry to manage its dependencies. Ensure you have Poetry installed and then run `poetry install` to install all required packages.

For more information on using Poetry, visit the [official documentation](https://python-poetry.org/docs/).


## Getting Started

Follow these instructions to get the system up and running.

### Replit Backend API
- Ensure the Replit backend API is active and running.

### Setup for Telegram
1. Open the Telegram app and start a chat with BotFather.
2. Create a new bot and note down the token provided.
    ```
    Use this token to access the HTTP API:
    [Your_Token]
    Keep your token secure and store it safely.
    ```
3. Update the `TOKEN` variable in `telegram_bot.py` with your new token.
4. Install the required package and run the bot:
    ```bash
    pip install python-telegram-bot
    python telegram_bot.py
    ```
5. In Telegram, search for your bot (e.g., `@socs_banking_bot`) and start interacting.

### Setup for Terminal (IPython)
1. Install IPython and python-dotenv:
    ```bash
    pip install IPython
    pip install python-dotenv
    ```
2. Open your terminal and start IPython by typing `ipython`.
3. Interact with the application in the IPython shell.

### Key Files
- `telegram_bot.py`
- `chat_bot.py`

