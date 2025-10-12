# run.ps1
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run "SEO Title and Hook Rewriter — fixed_optimized.py"

