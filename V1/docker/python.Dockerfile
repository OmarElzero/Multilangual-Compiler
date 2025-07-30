# Python Runtime Dockerfile
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 runner && \
    mkdir -p /app && \
    chown runner:runner /app

# Set working directory
WORKDIR /app

# Switch to non-root user
USER runner

# Set execution timeout (can be overridden)
ENV TIMEOUT=30

# Default command
CMD ["python3"]
