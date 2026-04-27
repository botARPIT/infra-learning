#!/bin/bash
set -e

cd ~/infra-learning

echo "Pulling latest code..."
git fetch origin main
git reset --hard origin/main

if [ -z "$DATABASE_URL" ] || [ -z "$REDIS_HOST" ]; then
  echo "Missing required secrets"
  exit 1
fi

cat > .env.runtime <<EOF
DATABASE_URL=$DATABASE_URL
REDIS_HOST=$REDIS_HOST
EOF

docker system prune -af || true

echo "Building fresh image..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml build

echo "Running migrations..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml run --rm api alembic upgrade head

echo "Stopping old services..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml down --remove-orphans

echo "Starting new services..."
docker compose -f docker-compose.base.yml -f docker-compose.vpc.yml up -d --remove-orphans

for i in {1..10}; do
  if curl -f http://localhost:8002/ready; then
    echo "Deploy complete"
    exit 0
  fi
  echo "Waiting for readiness..."
  sleep 3
done

echo "Deploy failed"
exit 1