#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/../../contract_fixture.py" "$PWD"
