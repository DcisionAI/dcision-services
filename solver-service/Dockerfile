# Build stage
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn

# Copy application code
COPY src/ src/
COPY setup.py .
RUN pip install -e .

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /build/src/ /app/src/

# Install gunicorn and uvicorn in the final stage (force reinstall to ensure binaries are present)
RUN pip install --force-reinstall gunicorn uvicorn

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8080

# Run the application with gunicorn and uvicorn workers
CMD ["gunicorn", "src.api.routes:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"] 