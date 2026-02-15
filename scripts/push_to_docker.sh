#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DOCKERHUB_REPO:-}" ]; then
  echo "Usage: DOCKERHUB_REPO=owner/repo ./scripts/push_to_docker.sh [tag]"
  exit 1
fi

TAG="${1:-latest}"
IMAGE="${DOCKERHUB_REPO}:${TAG}"

echo "Building ${IMAGE}..."
docker build -t "${IMAGE}" .

echo "Pushing ${IMAGE}..."
docker push "${IMAGE}"

echo "Done: ${IMAGE}"
