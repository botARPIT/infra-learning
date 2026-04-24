#!/bin/bash

set -e

echo "Updating packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl docker.io

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Docker..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Starting Redis..."
sudo docker run -d --name async-job-redis -p 6379:6379 redis:7-alpine || true

echo "Starting Postgres..."
sudo docker run -d 
--name async-job-postgres 
-p 5432:5432 
-e POSTGRES_USER=admin 
-e POSTGRES_PASSWORD=admin 
-e POSTGRES_DB=jobs 
postgres:16 || true

echo "Waiting for containers..."
sleep 5

echo "Starting API..."
python3 -m uvicorn api.app.main:app --host 0.0.0.0 --port 8002 &

echo "Starting worker 1..."
python3 -m api.worker.run &

echo "Starting worker 2..."
python3 -m api.worker.run &

echo "Starting reaper..."
python3 -m api.reaper.reaper &

sleep 3

echo "Health check..."
curl http://127.0.0.1:8002/health

echo "Metrics check..."
curl http://127.0.0.1:8002/metrics

wait
