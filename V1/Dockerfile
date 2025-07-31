# Multi-Language Execution Environment for PolyRun
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for all languages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get update && apt-get install -y nodejs
RUN node --version && npm --version

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "web/backend/modern_server.py", "--host", "0.0.0.0", "--port", "8000"]
