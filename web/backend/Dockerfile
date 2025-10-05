# Multi-stage Dockerfile for FastAPI backend
# Uses Python 3.12 slim image for optimal size and performance

FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size by not storing pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000 for FastAPI application
EXPOSE 8000

# Health check to ensure container is running properly
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/healthz || exit 1

# Run the FastAPI application with uvicorn
# --host 0.0.0.0 allows external connections (required for Docker)
# --port 8000 matches the exposed port
# --reload enables auto-reload in development (remove for production)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
