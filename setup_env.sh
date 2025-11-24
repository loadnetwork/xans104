#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate

pip install --upgrade pip
pip install -e .

# tests/run_hf_inference.py requirements
# pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.6.0"
# pip install transformers
