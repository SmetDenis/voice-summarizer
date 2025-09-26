# Voice Summarizer

CLI Tool for automatic transcription of audio and video files with the ability to create text summaries. Uses OpenAI API for media file processing.

[🇷🇺 Русская версия](README_RUS.md)

## System Requirements

- Python 3.12 or higher
- `uv` dependency manager
- Installed system utilities: `ffmpeg` and `ffprobe`
- Active OpenAI API key
- (Optional) AWS S3 credentials for downloading files from S3 buckets

## Installation

### 1. Installing System Dependencies

**macOS (via Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download ffmpeg from the official website https://ffmpeg.org/download.html

### 2. Installing Python Dependencies

```bash
# Installing project dependencies
uv sync
```

### 3. Environment Variables Configuration

```bash
# Copying configuration template
cp .env.example .env

# Editing configuration
nano .env
```

Fill in the following parameters in the `.env` file:

```bash
# OpenAI API Configuration (required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_WHISPER_MODEL=whisper-1
OPENAI_SUMMARY_MODEL=gpt-4o

# AWS S3 Configuration (optional, for S3 file downloads)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_DEFAULT_REGION=us-east-1
# AWS_ENDPOINT_URL=http://localhost:9000  # For MinIO or other S3-compatible services
```

## Project Structure

```
voice-summarizer/
├── main.py                  # Main transcription script
├── summarization_prompt.md  # Prompt template for summarization
├── .env.example            # Configuration example
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose configuration
├── input/                  # Directory for input files
└── output/                 # Directory for results
```

## Usage

### Basic Transcription

```bash
# Transcribing a local file
python main.py input/recording.mp4

# Transcribing a file from S3 bucket
python main.py s3://your-bucket/path/to/recording.mp4

# Specifying custom output directory
python main.py input/recording.mp4 -o custom_output
```

### Transcription with Summarization

```bash
# Transcription with automatic summary creation (local file) - default behavior
python main.py input/recording.mp4

# Transcription with automatic summary creation (S3 file) - default behavior
python main.py s3://your-bucket/path/to/recording.mp4

# Using custom prompt for summarization
python main.py input/recording.mp4 --prompt-file custom_prompt.md

# Disable summarization (transcription only)
python main.py input/recording.mp4 --no-summarize
```

### Model Configuration

```bash
# Specifying specific Whisper model
python main.py input/recording.mp4 --whisper-model whisper-1

# Specifying summarization model
python main.py input/recording.mp4 --summary-model gpt-4

# Full configuration with custom parameters
python main.py input/recording.mp4 \
    --whisper-model whisper-1 \
    --summary-model gpt-4 \
    --prompt-file my_prompt.md \
    --api-key YOUR_API_KEY \
    --base-url https://custom-endpoint.com/v1

# Transcription only (no summary)
python main.py input/recording.mp4 --no-summarize
```

## Docker Usage

Ready-made configurations are provided for users who prefer Docker.

### Quick Start with Docker

```bash
# 1. Environment preparation
cp .env.example .env
# Edit the .env file with your OpenAI API key

# 2. Place audio/video files in the input/ directory
cp your-recording.mp4 input/

# 3. Build and run with Docker Compose
docker-compose build
docker-compose run --rm voice-summarizer input/your-recording.mp4
```

### Manual Docker Image Build

```bash
# Building the image
docker build -t voice-summarizer .

# Running the container
docker run -v $(pwd)/input:/app/input:ro \
           -v $(pwd)/output:/app/output \
           -v $(pwd)/.env:/app/.env:ro \
           voice-summarizer input/your-file.mp4
```

### Docker Compose Commands

```bash
# Show help
docker-compose run --rm voice-summarizer --help

# Basic transcription with summarization (default)
docker-compose run --rm voice-summarizer input/recording.mp4

# Transcription only (no summarization)
docker-compose run --rm voice-summarizer input/recording.mp4 --no-summarize

# Using custom model
docker-compose run --rm voice-summarizer input/recording.mp4 \
    --whisper-model whisper-1 \
    --summary-model gpt-4

# Development mode (interactive shell)
docker-compose run --rm voice-summarizer-dev
```

## Command Line Parameters

| Parameter | Description |
|-----------|-------------|
| `input_file` | Path to input audio/video file or S3 URL (s3://bucket/key) |
| `-o, --output` | Directory for saving results (default: output) |
| `--api-key` | OpenAI API key (alternative to OPENAI_API_KEY variable) |
| `--base-url` | Base URL for OpenAI API (alternative to OPENAI_BASE_URL variable) |
| `--whisper-model` | Whisper model for transcription (default: whisper-1) |
| `--summary-model` | Model for summary creation (default: gpt-4o) |
| `--no-summarize` | Disable text summary creation (default: enabled) |
| `--prompt-file` | Path to summarization prompt file (default: summarization_prompt.md) |

## Output File Structure

After processing, the following directory structure is created:

```
output/
└── filename.ext/
    ├── filename_combined.md              # Combined transcription
    ├── filename_summary.md               # Summary (if enabled)
    └── segments/
        ├── filename_segment_001.mp3      # Audio segment 1
        ├── filename_segment_001.md       # Segment 1 transcription
        ├── filename_segment_002.mp3      # Audio segment 2
        └── filename_segment_002.md       # Segment 2 transcription
```

## Supported File Formats

The tool supports all formats compatible with ffmpeg:

**Audio:** MP3, WAV, FLAC, AAC, OGG, M4A
**Video:** MP4, AVI, MOV, MKV, WMV, FLV

## Technical Features

- Maximum segment duration: 570 seconds (9.5 minutes)
- Automatic splitting of long files into segments
- Conversion of all segments to MP3 format
- S3 support for downloading files from AWS S3 or compatible services (MinIO, etc.)
- Intelligent caching: reuse existing local files and segments to avoid reprocessing
- Process logging with timestamps
- Comprehensive error handling for API, file operations, and S3 access

## S3 Configuration

The tool supports downloading files from AWS S3 or S3-compatible services:

### AWS S3 Setup
1. Configure AWS credentials in `.env` file:
```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
```

2. Use S3 URLs in your commands:
```bash
python main.py s3://your-bucket/path/to/file.mp4
```

### MinIO or Custom S3 Services
For MinIO or other S3-compatible services, add the endpoint URL:
```bash
AWS_ENDPOINT_URL=http://localhost:9000
```

### S3 Features
- Files are downloaded to `input/` directory and cached locally
- Existing local files are reused to avoid re-downloading
- Supports both AWS S3 and S3-compatible services
- Works without S3 configuration when using local files only

## Creating Custom Prompts

To create your own summarization prompt:

1. Copy the `summarization_prompt.md` file
2. Modify the content according to requirements
3. The prompt is used as a system message, transcription text is passed separately
4. Specify the file path via the `--prompt-file` parameter or `PROMPT_FILE` environment variable

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
