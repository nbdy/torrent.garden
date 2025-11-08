#!/usr/bin/env bash
set -euo pipefail

# Build script for torrent_garden frontend and backend Docker images (arm64 by default)
# This script uses Reflex export zips to build separate images.
#
# Usage:
#   ./build.sh [IMAGE_BASE_NAME] [TAG]
# Defaults:
#   IMAGE_BASE_NAME: torrent_garden
#   TAG:             latest
# Env:
#   PLATFORM    Target platform for buildx (default: linux/arm64)
# Examples:
#   ./build.sh                             # builds torrent_garden-frontend:latest and torrent_garden-backend:latest
#   ./build.sh my/app v1.2.3               # builds my/app-frontend:v1.2.3 and my/app-backend:v1.2.3
#   PLATFORM=linux/amd64 ./build.sh        # override platform

IMAGE_BASE_NAME="${1:-torrent_garden}"
IMAGE_TAG="${2:-latest}"
PLATFORM="${PLATFORM:-linux/arm64}"

BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"

FRONTEND_IMAGE="${IMAGE_BASE_NAME}-frontend"
BACKEND_IMAGE="${IMAGE_BASE_NAME}-backend"

# Cleanup exported artifacts (zips and export dir) when the script exits
cleanup() {
  rm -rf export frontend.zip backend.zip || true
}
trap cleanup EXIT

check_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: $1 is not installed or not in PATH" >&2
    exit 1
  fi
}

check_cmd docker
check_cmd unzip

if ! docker buildx version >/dev/null 2>&1; then
  echo "Error: docker buildx is not available. Please install/enable Buildx (Docker 19.03+)." >&2
  exit 1
fi

# 1) Export frontend and backend zips using Reflex
if command -v uv >/dev/null 2>&1; then
  echo "Exporting Reflex app via 'uv run reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker' ..."
  uv run reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker
elif command -v reflex >/dev/null 2>&1; then
  echo "Exporting Reflex app via 'reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker' ..."
  reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker
else
  echo "Error: neither 'uv' nor 'reflex' is available to perform export." >&2
  exit 1
fi

# 2) Unpack zips into export directories
rm -rf export
mkdir -p export/frontend export/backend

if [[ ! -f frontend.zip || ! -f backend.zip ]]; then
  echo "Error: frontend.zip or backend.zip not found after export." >&2
  exit 1
fi

unzip -o frontend.zip -d export/frontend >/dev/null
unzip -o backend.zip -d export/backend >/dev/null

# 3) Build images
#    - Backend: uses Dockerfile contained in the exported backend bundle.

echo "Building ${BACKEND_IMAGE}:${IMAGE_TAG} for platform ${PLATFORM} using buildx (single-arch, --load) with docker/backend/Dockerfile..."
docker buildx build \
  --platform "${PLATFORM}" \
  --load \
  --label org.opencontainers.image.title="${BACKEND_IMAGE}" \
  --label org.opencontainers.image.version="${IMAGE_TAG}" \
  --label org.opencontainers.image.revision="${GIT_COMMIT}" \
  --label org.opencontainers.image.created="${BUILD_DATE}" \
  -t "${BACKEND_IMAGE}:${IMAGE_TAG}" \
  -t "${BACKEND_IMAGE}:arm64" \
  -f docker/backend/Dockerfile \
  .


echo "Built images: ${FRONTEND_IMAGE}:${IMAGE_TAG} and ${BACKEND_IMAGE}:${IMAGE_TAG} (also tagged :arm64) for ${PLATFORM}"