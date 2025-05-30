#!/usr/bin/env bash
set -e

# Start TorchServe in the background
# Use the config file for model loading if possible, or specify models here
# For simplicity, and since your config.properties has load_models=all,
# we can rely on that, or be explicit here.
# Let's be explicit to match your model file name 'where.mar'.
echo "INFO: Starting TorchServe with model where=where.mar"
torchserve --start \
  --model-store /model-store \
  --models where=where.mar \
  --ncs & # ncs = no config snapshot
TS_PID=$!

# It's better to wait for TorchServe to be ready by polling its health endpoint
# rather than a fixed sleep. However, for simplicity, we'll keep sleep for now
# but acknowledge it's not the most robust way.
echo "INFO: Waiting for TorchServe to initialize..."
sleep 15 # Increased sleep slightly, adjust as needed or implement polling

echo "INFO: Starting FastAPI on port 8000"
# Start FastAPI on port 8000 to avoid conflict with TorchServe's management port (8081)
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload