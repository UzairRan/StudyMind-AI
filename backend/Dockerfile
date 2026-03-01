# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PDF processing and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    poppler-utils \        # For pdfplumber
    libgl1-mesa-glx \       # For some ML dependencies
    libglib2.0-0 \          # System utilities
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (leverages Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p vector_store temp_uploads && \
    chmod 777 vector_store temp_uploads

# Health check for Render
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with production settings
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 