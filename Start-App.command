#!/bin/bash
set -e
cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
else
  python -m pip install streamlit pandas numpy
fi

python -m streamlit run app.py
