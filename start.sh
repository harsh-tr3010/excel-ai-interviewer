#!/bin/bash

# Activate virtual environment
source ./venv/bin/activate

# Install dependencies just in case (optional for first deploy)
pip install -r requirements.txt

# Start the Gradio app via Uvicorn
uvicorn app.gui:demo --host 0.0.0.0 --port $PORT
