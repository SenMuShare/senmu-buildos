#!/bin/sh
set -eu
python3 "$(dirname "$0")/../contract_pipeline_workspace.py" "$PWD" contract-baseline
