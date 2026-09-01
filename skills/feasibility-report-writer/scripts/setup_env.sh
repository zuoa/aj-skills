#!/usr/bin/env bash
# Create a local venv and install the feasibility-report-writer dependencies.
# Reuses the project venv path (.venv at skill root) convention from sibling skills.
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
    echo "dependency install failed in strict mode" >&2
    exit 1
  fi
  echo "warning: dependency install failed (likely offline)." >&2
  echo "warning: venv is created, but some scripts may run in fallback mode." >&2
fi

# Step 2: check pandoc (needed by pypandoc for DOCX output).
if ! command -v pandoc >/dev/null 2>&1; then
  echo "warning: pandoc is not installed. DOCX conversion via pypandoc will fail." >&2
  echo "warning: install pandoc, e.g. on macOS: brew install pandoc" >&2
else
  echo "pandoc: $(pandoc --version | head -1)"
fi

echo "venv ready: ${VENV_DIR}"
echo "run scripts with: ${VENV_DIR}/bin/python scripts/<script>.py"
