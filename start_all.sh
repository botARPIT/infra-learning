#!/bin/bash

set -e

echo "Updating packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl docker.io

echo "Starting Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "Cleaning old Redis container if exists..."
sudo docker rm -f async-job-redis 2>/dev/null || true

echo "Starting Redis..."
sudo docker run -d \
  --name async-job-redis \
  -p 6379:6379 \
  redis:7-alpine

echo "Cleaning old Postgres container if exists..."
sudo docker rm -f async-job-postgres 2>/dev/null || true

echo "Starting Postgres..."
sudo docker run -d \
  --name async-job-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=jobs \
  postgres:16

echo "Waiting for infra containers..."
sleep 5

echo "Starting API..."
./venv/bin/python -m uvicorn api.app.main:app --host 0.0.0.0 --port 8002 > api.log 2>&1 &

echo "Starting worker 1..."
./venv/bin/python -m api.worker.run > worker1.log 2>&1 &

echo "Starting worker 2..."
./venv/bin/python -m api.worker.run > worker2.log 2>&1 &

echo "Starting reaper..."
./venv/bin/python -m api.reaper.reaper > reaper.log 2>&1 &

echo "Waiting for services..."
sleep 3

echo "Health check..."
curl http://127.0.0.1:8002/health

echo ""
echo "Metrics check..."
curl http://127.0.0.1:8002/metrics

echo ""
echo "Bootstrap complete."
echo "Logs:"
echo "  api.log"
echo "  worker1.log"
echo "  worker2.log"
echo "  reaper.log"

wait