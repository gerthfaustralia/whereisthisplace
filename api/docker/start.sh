#!/usr/bin/env bash
set -e

# Start TorchServe in the background
torchserve --start \
  --model-store /model-store \
  --models where=where-v1.mar \
  --ncs &                       # ncs = no config snapshot
TS_PID=$!

# Give it a few seconds to load the model
sleep 5

# Start FastAPI on 8081
exec uvicorn api.main:app --host 0.0.0.0 --port 8081
