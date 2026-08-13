#!/usr/bin/env bash
set -e

if [ -f "./venv/bin/uvicorn" ]; then
    UVICORN="./venv/bin/uvicorn"
else
    UVICORN="uvicorn"
fi

echo "Starting Automated Content Factory backend server..."
$UVICORN backend.main:app --reload --host 0.0.0.0 --port 8000
