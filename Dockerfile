# -------------------------------
# Base image (CPU-only, stable)
# -------------------------------
FROM python:3.11-slim

# -------------------------------
# Environment optimizations
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# -------------------------------
# Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# System dependencies (required for torch / sentence-transformers)
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Copy requirements first (Docker cache)
# -------------------------------
COPY requirements.txt .

# -------------------------------
# Install Python dependencies
# -------------------------------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copy application code
# -------------------------------
COPY . .

# -------------------------------
# Expose FastAPI port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Start FastAPI
# -------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
