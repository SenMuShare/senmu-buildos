#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/../../workspace_fixture.py" "$PWD" hard-bug
