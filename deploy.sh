#!/bin/bash
set -e

cd ~/infra-learning

echo "Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "Building fresh image..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml build

echo "Running migrations..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml run --rm api alembic upgrade head

echo "Restarting services..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml up -d --remove-orphans

echo "Checking health..."
curl -f http://localhost:8002/health

echo "Deploy complete"