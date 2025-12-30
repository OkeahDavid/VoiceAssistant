# Docker Deployment Guide

This document explains how to build and run the Voice Assistant using Docker.

## Prerequisites

- Docker installed on your system
- Internet connection for downloading dependencies

## Building the Docker Image

From the project directory:

```bash
docker build -t voice-assistant .
```

This will:
1. Create a Python 3.10 environment
2. Install system dependencies (ffmpeg, portaudio, build tools)
3. Install all Python packages from requirements.txt
4. Copy the application code

Build time: ~10-15 minutes (depending on internet speed)
Image size: ~8-9 GB (includes PyTorch and CUDA libraries)

## Running the Container

### Interactive Mode

```bash
docker run -it --rm voice-assistant
```

This starts the assistant in interactive text mode. You can type commands and receive responses.

**Example Session:**
```
A: Hello! I'm your voice assistant. I can help you with weather information and calendar management.
You: What will the weather be like today in Marburg?
Assistant: On Tuesday in Marburg, the weather will be snow with temperatures between -5°C and 5°C.
You: exit
Assistant: Goodbye! Have a great day!
```

### Batch Mode (with Piped Input)

```bash
echo -e "What's the weather in Hamburg?\nexit" | docker run -i --rm voice-assistant
```

## Docker Run Options

- `-it`: Interactive mode with TTY (terminal)
- `-i`: Interactive mode (for piped input)
- `--rm`: Automatically remove container when it exits
- `--name <name>`: Give the container a custom name

## Container Behavior

### What's Inside
- Python 3.10.16
- Whisper ASR model (base) - auto-downloads on first use (~140MB)
- PyTorch 2.9.1 with CUDA support
- All required dependencies

### Limitations
- **No voice mode**: Containers don't support audio I/O, so the assistant runs in `--no-voice` mode
- **Text input only**: All commands must be typed
- **Model download**: First run downloads Whisper model (~140MB)

### Calendar Data
- Each container instance creates a unique session-based calendar ID
- Calendar data is stored on the API server, not in the container
- Appointments persist across container restarts if you query the same day

## Troubleshooting

### Build Failures

**Problem**: PyAudio build fails
```
Solution: Ensure build-essential and gcc are in the Dockerfile
```

**Problem**: Out of disk space
```
Solution: Docker images are large (~9GB). Check available space:
  docker system df
  docker system prune  # Clean up unused images
```

### Runtime Issues

**Problem**: "Module not found" errors
```
Solution: Rebuild the image:
  docker build --no-cache -t voice-assistant .
```

**Problem**: Slow first run
```
Explanation: Whisper model downloads on first use (~140MB)
  Subsequent runs are faster
```

## Advanced Usage

### Custom Configuration

To modify the default command:

```bash
# Run with voice mode enabled (won't work without audio, but for testing)
docker run -it --rm voice-assistant python main.py

# Run test suite
docker run -it --rm voice-assistant python test_assistant.py
```

### Saving Model for Faster Startup

```dockerfile
# Add to Dockerfile before CMD
RUN python -c "import whisper; whisper.load_model('base')"
```

This pre-downloads the Whisper model into the image (increases image size by 140MB).

### Mounting Local Code

For development, mount your local code:

```bash
docker run -it --rm \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/main.py:/app/main.py \
  voice-assistant
```

Changes to local files will be reflected in the container.

## Production Deployment

### Using Docker Compose

See [docker-compose.yml](docker-compose.yml) for orchestration.

```bash
docker-compose up
```

### Cloud Deployment

The container can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Any Docker-compatible hosting

**Note**: Voice mode won't work in cloud environments. Use text mode only.

## Performance

### Resource Usage
- **Memory**: ~4GB minimum (PyTorch + models)
- **CPU**: Multi-core recommended
- **Storage**: ~9GB for image + ~500MB runtime

### First Run vs Subsequent Runs
- **First run**: 30-60 seconds (Whisper model download + initialization)
- **Subsequent runs**: 10-20 seconds (initialization only)

## Security Notes

- Container runs as root by default
- No sensitive data stored in container
- API calls use HTTP (not production-ready for sensitive data)
- Calendar ID is session-based and not secret

## Verification

To verify the build succeeded:

```bash
# Check image exists
docker images voice-assistant

# Check installed packages
docker run --rm voice-assistant pip list

# Run quick test
echo -e "test\nexit" | docker run -i --rm voice-assistant
```

## Cleanup

Remove the image:
```bash
docker rmi voice-assistant
```

Remove all Docker artifacts:
```bash
docker system prune -a
```

## Support

For issues:
1. Check logs: Container output shows all errors
2. Verify build: `docker build` should complete without errors
3. Test locally: Run without Docker first to isolate issues

---

**Last Updated**: December 30, 2024
**Docker Version**: Tested with Docker 28.2.2
**Base Image**: python:3.10-slim
