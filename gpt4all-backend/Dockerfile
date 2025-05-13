FROM python:3.10-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove model copy; model will be downloaded from GCS at runtime
# ARG MODEL_FILENAME=DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf
# COPY models/${MODEL_FILENAME} .

# Copy application code
COPY main.py .

# Expose port and start server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]