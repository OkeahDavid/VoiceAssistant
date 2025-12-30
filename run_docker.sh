#!/bin/bash

# Build Docker image
echo "Building Docker image..."
docker build -t voice-assistant .

# Run Docker container in interactive mode
echo "Running voice assistant in Docker..."
docker run -it --rm voice-assistant
