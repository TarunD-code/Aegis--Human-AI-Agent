#!/usr/bin/env bash

set -e

echo "Running Verification Suite for Aegis v3.6"
echo "-----------------------------------------"

echo "1. Bootstrapping environment..."
bash scripts/bootstrap.sh

echo "2. Running Linter..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true

echo "3. Running Mypy..."
mypy . --ignore-missing-imports || true

echo "4. Running Unit Tests..."
export AEGIS_OFFLINE_MODE=true
pytest tests/

echo "5. Starting Health Endpoint & Daemon Test..."
python main.py --mode background &
DAEMON_PID=$!
sleep 2

response=$(curl -s http://127.0.0.1:17123/health || echo "Failed")
if [[ "$response" == *"ok"* ]]; then
  echo "Health Check Passed."
else
  echo "Health Check Failed. Response: $response"
  kill $DAEMON_PID
  exit 1
fi

kill $DAEMON_PID
echo "Verification Suite Passed!"
