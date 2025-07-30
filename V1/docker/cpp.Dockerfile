# C++ Runtime Dockerfile
FROM gcc:latest

# Install minimal dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libc6-dev && \
    rm -rf /var/lib/apt/lists/*

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
CMD ["g++"]
