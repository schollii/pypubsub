#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${1:-python}"

echo "Using Python executable: ${python_bin}"

run_example() {
  local title="$1"
  shift
  echo
  echo "### ${title}"
  (cd "${script_dir}/$1" && shift && "${python_bin}" "$@")
}

run_example "basic_kwargs/console_main.py" basic_kwargs console_main.py
run_example "advanced/advanced_main.py" advanced advanced_main.py

if "${python_bin}" -c "import wx" >/dev/null 2>&1; then
  run_example "basic_kwargs/wx_main.py" basic_kwargs wx_main.py
else
  echo
  echo "Skipping wx example (wxPython not installed)."
fi
