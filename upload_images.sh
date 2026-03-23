#!/bin/bash

set -e

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

REGISTRY="${REGISTRY_URL}"
PASSWORD="${REGISTRY_PASSWORD}"
USERNAME="${REGISTRY_USERNAME}"
TAG="${IMAGE_TAG:-latest}"

if [ -z "$REGISTRY" ] || [ -z "$PASSWORD" ] || [ -z "$USERNAME" ]; then
  echo "Error: REGISTRY_URL, REGISTRY_PASSWORD, and REGISTRY_USERNAME must be defined in .env file."
  exit 1
fi

echo "Logging in to $REGISTRY..."
echo "$PASSWORD" | docker login "$REGISTRY" -u "$USERNAME" --password-stdin

echo "========================================"
echo "Building Container Images..."
echo "========================================"

docker build --platform linux/amd64 -t "$REGISTRY/soccer-job-api:${TAG}" -f src/backend/Dockerfile.job-api src/backend
docker build --platform linux/amd64 -t "$REGISTRY/soccer-persist-api:${TAG}" -f src/backend/Dockerfile.persist-api src/backend
docker build --platform linux/amd64 -t "$REGISTRY/soccer-job-worker:${TAG}" -f src/backend/Dockerfile.job-worker src/backend
docker build --platform linux/amd64 -t "$REGISTRY/soccer-persist-worker:${TAG}" -f src/backend/Dockerfile.persist-worker src/backend
docker build --platform linux/amd64 -t "$REGISTRY/soccer-beat:${TAG}" -f src/backend/Dockerfile.beat src/backend
docker build --platform linux/amd64 -t "$REGISTRY/soccer-frontend:${TAG}" -f src/frontend/Dockerfile src/frontend

echo "========================================"
echo "Pushing Container Images..."
echo "========================================"

docker push "$REGISTRY/soccer-job-api:${TAG}"
docker push "$REGISTRY/soccer-persist-api:${TAG}"
docker push "$REGISTRY/soccer-job-worker:${TAG}"
docker push "$REGISTRY/soccer-persist-worker:${TAG}"
docker push "$REGISTRY/soccer-beat:${TAG}"
docker push "$REGISTRY/soccer-frontend:${TAG}"

echo "========================================"
echo "All images pushed successfully!"
echo "========================================"
