# Voice Summarizer Docker Image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for faster Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application files
COPY main.py ./
COPY summarization_prompt.md ./
COPY .env.example ./

# Create directories for input and output
RUN mkdir -p input output

# Set the default command
ENTRYPOINT ["uv", "run", "python", "main.py"]
CMD ["--help"]

# Labels for metadata
LABEL maintainer="Voice Summarizer"
LABEL description="Audio/Video transcription tool with AI summarization"
LABEL version="0.1.0"
