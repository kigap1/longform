#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"
ENV_FILE="$ROOT_DIR/.env"

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-3000}"

load_env_file() {
  if [[ ! -f "$ENV_FILE" ]]; then
    return
  fi

  while IFS='=' read -r raw_key raw_value; do
    local key value
    key="$(printf '%s' "$raw_key" | sed 's/[[:space:]]*$//')"
    value="$raw_value"

    if [[ -z "$key" ]] || [[ "$key" =~ ^[[:space:]]*# ]]; then
      continue
    fi

    if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      continue
    fi

    if [[ -z "${!key+x}" ]]; then
      export "$key=$value"
    fi
  done < "$ENV_FILE"
}

resolve_python() {
  if [[ -x "$API_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$API_DIR/.venv/bin/python"
    return
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  printf 'python3 not found. Please install Python 3.11+.\n' >&2
  exit 1
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [[ -n "${frontend_pid:-}" ]] && kill -0 "$frontend_pid" 2>/dev/null; then
    kill "$frontend_pid" 2>/dev/null || true
  fi

  if [[ -n "${backend_pid:-}" ]] && kill -0 "$backend_pid" 2>/dev/null; then
    kill "$backend_pid" 2>/dev/null || true
  fi

  wait "${frontend_pid:-}" 2>/dev/null || true
  wait "${backend_pid:-}" 2>/dev/null || true
  exit "$exit_code"
}

load_env_file

if ! command -v pnpm >/dev/null 2>&1; then
  printf 'pnpm not found. Please install pnpm first.\n' >&2
  exit 1
fi

PYTHON_BIN="$(resolve_python)"
export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://$API_HOST:$API_PORT/api}"

trap cleanup EXIT INT TERM

printf 'Starting API on http://%s:%s\n' "$API_HOST" "$API_PORT"
(
  cd "$API_DIR"
  exec "$PYTHON_BIN" -m uvicorn app.main:app --reload --host "$API_HOST" --port "$API_PORT"
) &
backend_pid=$!

printf 'Starting web on http://%s:%s\n' "$WEB_HOST" "$WEB_PORT"
(
  cd "$WEB_DIR"
  exec pnpm exec next dev --hostname "$WEB_HOST" --port "$WEB_PORT"
) &
frontend_pid=$!

printf 'Both servers are running. Press Ctrl+C to stop them together.\n'

while true; do
  if ! kill -0 "$backend_pid" 2>/dev/null; then
    wait "$backend_pid"
    exit $?
  fi

  if ! kill -0 "$frontend_pid" 2>/dev/null; then
    wait "$frontend_pid"
    exit $?
  fi

  sleep 1
done
