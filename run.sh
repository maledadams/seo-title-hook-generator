#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Change the filename below if you rename the app file
python -m streamlit run "Seo Title And Hook Rewriter — App"
