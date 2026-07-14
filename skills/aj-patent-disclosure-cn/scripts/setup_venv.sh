#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "warning: scripts/setup_venv.sh is deprecated; use scripts/setup_env.sh"
exec bash "${ROOT_DIR}/scripts/setup_env.sh" "$@"
