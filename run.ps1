# One-click local run on Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Change the filename below if you rename the app file
python -m streamlit run "Seo Title And Hook Rewriter — App"
