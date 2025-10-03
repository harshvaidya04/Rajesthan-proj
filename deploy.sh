#!/bin/bash
# Step 1: Update system
sudo apt update && sudo apt upgrade -y

# Step 2: Install Python dependencies
pip install fastapi uvicorn pandas openpyxl xlrd

# Step 3: Run FastAPI app
uvicorn main:app --host 0.0.0.0 --port 8000
