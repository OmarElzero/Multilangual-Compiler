#!/bin/bash
# Build Docker images for PolyRun

echo "🐳 Building PolyRun Docker Images..."

# Build Python image
echo "Building Python runtime image..."
docker build -f docker/python.Dockerfile -t polyrun-python:latest .

# Build C++ image  
echo "Building C++ runtime image..."
docker build -f docker/cpp.Dockerfile -t polyrun-cpp:latest .

# List created images
echo "✅ Docker images created:"
docker images | grep polyrun

echo "🎯 Ready for secure code execution!"
