#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
STRICT_MODE=1
DEFAULT_PIP_INDEX_URL="https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
PIP_INDEX_URL="${PIP_INDEX_URL:-${DEFAULT_PIP_INDEX_URL}}"

if [[ "${1:-}" == "--allow-partial" ]]; then
  STRICT_MODE=0
fi

cd "${ROOT_DIR}"

# Step 1: create venv and install dependencies.
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip -i "${PIP_INDEX_URL}"
if ! "${VENV_DIR}/bin/pip" install -r "${ROOT_DIR}/requirements.txt" -i "${PIP_INDEX_URL}"; then
  if [[ "${STRICT_MODE}" -eq 1 ]]; then
    echo "dependency install failed in strict mode"
    exit 1
  fi
  echo "warning: dependency install failed (likely offline)."
  echo "warning: venv is created, but some scripts may run in fallback mode."
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "warning: pandoc is not installed. DOCX conversion via pypandoc will fail."
  echo "warning: install pandoc, e.g. on macOS: brew install pandoc"
fi

# Step 2: preflight dependency check.
if [[ "${STRICT_MODE}" -eq 1 ]]; then
  "${VENV_DIR}/bin/python" scripts/check_dependencies.py --task all --strict
else
  "${VENV_DIR}/bin/python" scripts/check_dependencies.py --task all || true
fi

echo ""
echo "Environment initialized."
echo "venv ready: ${VENV_DIR}"
echo "pip index: ${PIP_INDEX_URL}"
if [[ "${STRICT_MODE}" -eq 1 ]]; then
  echo "mode: strict (default)"
else
  echo "mode: allow-partial"
fi
echo "Next: source .venv/bin/activate"
echo "Verify: which python"
