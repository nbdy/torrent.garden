#!/usr/bin/env bash
set -euo pipefail

# Deploy script to update server and related services in one go for split frontend/backend images.
# Ensures arm64 images are available locally (auto-builds with buildx if needed),
# exports both, uploads to remote, imports them there, then runs docker compose up -d.
#
# Usage:
#   ./deploy.sh <REMOTE> <REMOTE_PROJECT_DIR> [IMAGE_BASE_NAME] [TAG]
#
# Parameters:
#   REMOTE              SSH target in the form user@host (or host if configured)
#   REMOTE_PROJECT_DIR  Absolute path on remote where docker-compose.yml lives
#   IMAGE_BASE_NAME     (optional) defaults to torrent_garden
#   TAG                 (optional) defaults to latest
#
# Examples:
#   ./deploy.sh ubuntu@myserver /srv/torrent_garden
#   ./deploy.sh ubuntu@myserver /srv/torrent_garden my/app v1.2.3

usage() {
  sed -n '1,/$/p' "$0" | sed -n '1,31p' | sed 's/^# \{0,1\}//' >&2
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

for cmd in docker ssh scp rsync; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is not installed or not in PATH (local)" >&2
    exit 1
  fi
done

REMOTE="${1:?REMOTE (user@host) is required}"
REMOTE_DIR="${2:?REMOTE_PROJECT_DIR is required}"
IMAGE_BASE_NAME="${3:-torrent_garden}"
IMAGE_TAG="${4:-latest}"

FRONTEND_IMAGE="${IMAGE_BASE_NAME}-frontend"
BACKEND_IMAGE="${IMAGE_BASE_NAME}-backend"

# Ensure rsync is available on remote
if ! ssh "${REMOTE}" "command -v rsync >/dev/null 2>&1"; then
  echo "Error: rsync is not installed on remote host ${REMOTE}. Please install it (e.g., 'sudo apt-get install rsync')." >&2
  exit 1
fi

FRONTEND_ARCHIVE_NAME="${FRONTEND_IMAGE//\//_}_${IMAGE_TAG}.tar.gz"
BACKEND_ARCHIVE_NAME="${BACKEND_IMAGE//\//_}_${IMAGE_TAG}.tar.gz"

LOCAL_FRONTEND_ARCHIVE="${TMPDIR:-/tmp}/${FRONTEND_ARCHIVE_NAME}"
LOCAL_BACKEND_ARCHIVE="${TMPDIR:-/tmp}/${BACKEND_ARCHIVE_NAME}"

REMOTE_FRONTEND_ARCHIVE="/tmp/${FRONTEND_ARCHIVE_NAME}"
REMOTE_BACKEND_ARCHIVE="/tmp/${BACKEND_ARCHIVE_NAME}"

set -x
# 1) Ensure images exist locally; auto-build if missing either
if ! docker image inspect "${FRONTEND_IMAGE}:${IMAGE_TAG}" >/dev/null 2>&1 || \
   ! docker image inspect "${BACKEND_IMAGE}:${IMAGE_TAG}" >/dev/null 2>&1; then
  echo "One or both images not found locally. Building arm64 images via buildx..."
  PLATFORM=linux/arm64 ./build.sh "${IMAGE_BASE_NAME}" "${IMAGE_TAG}"
fi

# Prefer the requested tag, but fall back to :arm64 if necessary for each image
SAVE_TAG_FRONTEND="${IMAGE_TAG}"
SAVE_TAG_BACKEND="${IMAGE_TAG}"

if ! docker image inspect "${FRONTEND_IMAGE}:${SAVE_TAG_FRONTEND}" >/dev/null 2>&1; then
  if docker image inspect "${FRONTEND_IMAGE}:arm64" >/dev/null 2>&1; then
    SAVE_TAG_FRONTEND="arm64"
  else
    echo "Error: ${FRONTEND_IMAGE}:${IMAGE_TAG} not found locally after build." >&2
    exit 1
  fi
fi

if ! docker image inspect "${BACKEND_IMAGE}:${SAVE_TAG_BACKEND}" >/dev/null 2>&1; then
  if docker image inspect "${BACKEND_IMAGE}:arm64" >/dev/null 2>&1; then
    SAVE_TAG_BACKEND="arm64"
  else
    echo "Error: ${BACKEND_IMAGE}:${IMAGE_TAG} not found locally after build." >&2
    exit 1
  fi
fi

# 2) Determine whether images changed on remote (by tag) and decide uploads
LOCAL_BACKEND_ID=$(docker image inspect --format '{{.Id}}' "${BACKEND_IMAGE}:${SAVE_TAG_BACKEND}")

REMOTE_BACKEND_ID=$(ssh "${REMOTE}" "docker image inspect --format '{{.Id}}' '${BACKEND_IMAGE}:${SAVE_TAG_BACKEND}' 2>/dev/null" || true)

UPLOAD_BACKEND=1
if [[ -n "${REMOTE_BACKEND_ID}" && "${REMOTE_BACKEND_ID}" == "${LOCAL_BACKEND_ID}" ]]; then
  echo "Backend image ${BACKEND_IMAGE}:${SAVE_TAG_BACKEND} unchanged on remote. Skipping upload."
  UPLOAD_BACKEND=0
fi

# 3) Export/save changed images only
rm -f "${LOCAL_FRONTEND_ARCHIVE}" "${LOCAL_BACKEND_ARCHIVE}"
if [[ ${UPLOAD_BACKEND} -eq 1 ]]; then
  docker save "${BACKEND_IMAGE}:${SAVE_TAG_BACKEND}" | gzip > "${LOCAL_BACKEND_ARCHIVE}"
fi

# 3) Upload image archives to remote (only if created)
if [[ ${UPLOAD_BACKEND} -eq 1 ]]; then
  scp "${LOCAL_BACKEND_ARCHIVE}"  "${REMOTE}:${REMOTE_BACKEND_ARCHIVE}"
fi

# 3.5) Ensure remote project directory exists and sync compose-related files
ssh "${REMOTE}" bash -lc "\
  set -euo pipefail; \
  mkdir -p '${REMOTE_DIR}'; \
  mkdir -p '${REMOTE_DIR}/docker/caddy' '${REMOTE_DIR}/docker/valkey'; \
  for p in '${REMOTE_DIR}/docker/caddy/Caddyfile' '${REMOTE_DIR}/docker/valkey/valkey.conf'; do \
    if [ -d \"\$p\" ]; then rm -rf \"\$p\"; fi; \
  done \
"
rsync -az "docker-compose.yml" "${REMOTE}:${REMOTE_DIR}/docker-compose.yml"
if [[ -f ".env" ]]; then
  if ssh "${REMOTE}" "[[ -f '${REMOTE_DIR}/.env' ]]"; then
    echo "Remote .env exists at ${REMOTE_DIR}/.env - not overwriting."
  else
    rsync -az ".env" "${REMOTE}:${REMOTE_DIR}/.env"
  fi
fi
if [[ -d "docker" ]]; then
  rsync -az --delete "docker/" "${REMOTE}:${REMOTE_DIR}/docker/"
fi

# 3.6) Prepare and upload static frontend export for Caddy
if [[ ! -d "export/frontend" ]]; then
  echo "Preparing Reflex export for frontend static files..."
  if command -v uv >/dev/null 2>&1; then
    uv run reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker
  elif command -v reflex >/dev/null 2>&1; then
    reflex export --zip --env prod --exclude-from-backend data --exclude-from-backend docker
  else
    echo "Warning: neither 'uv' nor 'reflex' found; skipping export of frontend static assets." >&2
  fi
  if [[ -f "frontend.zip" ]]; then
    rm -rf export/frontend
    mkdir -p export/frontend
    unzip -o frontend.zip -d export/frontend >/dev/null
  fi
fi

ssh "${REMOTE}" bash -lc "\
  set -euo pipefail; \
  mkdir -p '${REMOTE_DIR}/export/frontend'; \
"
if [[ -d "export/frontend" ]]; then
  rsync -az --delete "export/frontend/" "${REMOTE}:${REMOTE_DIR}/export/frontend/"
else
  echo "Warning: export/frontend not found; Caddy will not have static files to serve." >&2
fi

# 4) Import/load on remote and clean up archives (if present), then update services
ssh "${REMOTE}" bash -lc "\
  set -euo pipefail; \
  if [ -f '${REMOTE_BACKEND_ARCHIVE}' ]; then docker load -i '${REMOTE_BACKEND_ARCHIVE}'; rm -f '${REMOTE_BACKEND_ARCHIVE}'; fi; \
  cd '${REMOTE_DIR}'; \
  docker compose pull valkey db || true; \
  docker compose up --remove-orphans -d; \
"
set +x

echo "Deployment completed successfully to ${REMOTE}:${REMOTE_DIR}"