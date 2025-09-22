#!/bin/bash

# Simple script to run the FastAPI backend
# Activates virtual environment and runs the backend

cd beanstalk_notion_service/backend
source .venv/bin/activate
fastapi run app/main.py --reload
