# FastAPI Chat Client Backend

## Overview
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
To run the application, use the following command:

```bash
poetry run uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000` by default.

## Environment Variables
The following environment variables are required for the project:

- `PROJECT_NAME`: The name of the project.
- `SENTRY_DSN`: The DSN for Sentry integration (optional).

These variables should be set in the `.env` file.

## Poetry Dependency Management
This project uses Poetry to manage its dependencies. Ensure you have Poetry installed and then run `poetry install` to install all required packages.

For more information on using Poetry, visit the [official documentation](https://python-poetry.org/docs/).
