#!/bin/bash

# Start FastAPI in the background
uvicorn app.api:app --host 0.0.0.0 --port 8000 &

# Start the scheduler
python scheduler.py