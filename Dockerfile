FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
# Change the filename below if you rename the app file
CMD ["streamlit", "run", "Seo Title And Hook Rewriter — App", "--server.port=8501", "--server.address=0.0.0.0"]
