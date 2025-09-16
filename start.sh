#!/bin/bash
# Activate virtual environment
source venv/bin/activate

# Run FastAPI app with auto-detected port
python -m uvicorn app.gui:demo --host 0.0.0.0 --port ${PORT:-8000}
