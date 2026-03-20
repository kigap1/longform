#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"

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

PYTHON_BIN="$(resolve_python)"

cd "$API_DIR"
exec "$PYTHON_BIN" -m unittest discover -s tests "$@"
