# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Voice Summarizer is an audio/video transcription tool that splits media files into segments and transcribes them using OpenAI's Whisper API. It can also generate summaries of the transcribed content using OpenAI's chat models. The main functionality is contained in `main.py`.

## Dependencies and Setup

- Python 3.12+ required
- Uses `uv` for dependency management
- External dependencies: `ffmpeg` and `ffprobe` (must be installed on system)
- OpenAI API key required
- Optional: AWS S3 credentials for downloading files from S3 buckets
- Docker support available for containerized deployment

Setup commands:
```bash
# Native Python setup
uv sync
cp .env.example .env
# Edit .env with your OpenAI API key, model preferences, and optionally AWS S3 credentials

# Docker setup (alternative)
cp .env.example .env
# Edit .env, then:
docker-compose build
docker-compose run --rm voice-summarizer --help
```

## Core Architecture

The application follows a single-class design centered around the `AudioTranscriber` class in `main.py`:

### AudioTranscriber Class Structure
- **Configuration Management**: Handles OpenAI API keys, base URLs, and model selection via environment variables or constructor parameters
- **S3 Integration**: Supports downloading files from AWS S3 or S3-compatible services (MinIO, etc.)
- **File Processing Pipeline**:
  1. `download_from_s3()` - Downloads files from S3 if S3 URL is provided
  2. `get_file_duration()` - Uses ffprobe to determine media duration
  3. `split_audio()` - Segments files into 9.5-minute chunks using ffmpeg
  4. `transcribe_audio()` - Calls OpenAI Whisper API for each segment
  5. `save_transcription()` - Saves individual segment transcriptions as markdown
  6. `process_file()` - Orchestrates the full pipeline and creates combined output
- **Security Features**: Path validation via `_validate_path()` prevents directory traversal attacks
- **Optional Summarization**: `summarize_transcription()` uses OpenAI chat models with customizable prompts

### Key Files
- **`main.py`**: Complete application with AudioTranscriber class and CLI interface
- **`summarization_prompt.md`**: English-language prompt template for AI summarization (generates structured meeting reports)
- **`Dockerfile`** + **`docker-compose.yml`**: Container deployment configuration
- **Directory structure**:
  - `input/` - Place audio/video files here
  - `output/` - Generated transcriptions organized by filename/segments/

## Common Commands

```bash
# Basic transcription (local file)
python main.py input/your-file.mp4

# Basic transcription (S3 file)
python main.py s3://your-bucket/path/to/your-file.mp4

# With output directory
python main.py input/your-file.mp4 -o custom_output

# With summarization (default behavior)
python main.py input/your-file.mp4

# S3 file with summarization (default behavior)
python main.py s3://your-bucket/path/to/your-file.mp4

# Transcription only (disable summarization)
python main.py input/your-file.mp4 --no-summarize

# Custom API settings
python main.py input/your-file.mp4 --api-key YOUR_KEY --base-url https://custom-api.com/v1 --whisper-model whisper-1

# Docker usage
docker-compose run --rm voice-summarizer input/your-file.mp4
docker-compose run --rm voice-summarizer s3://your-bucket/path/to/your-file.mp4
docker-compose run --rm voice-summarizer input/your-file.mp4 --no-summarize  # Transcription only
docker-compose run --rm voice-summarizer-dev  # Development shell
```

## Implementation Details

- **Segment Limits**: 570 seconds (9.5 minutes) maximum per segment for OpenAI's 25MB file limit
- **File Processing**: ffmpeg handles audio/video splitting and MP3 conversion
- **S3 Support**: Optional boto3 dependency enables S3 file downloads; files are downloaded to local `input/` directory before processing; existing local files are reused to avoid re-downloading; works without S3 configuration for local files only
- **Output Organization**: `output/filename.ext/` contains combined transcription, summary (if requested), and `segments/` subdirectory with individual audio files and transcriptions
- **Error Handling**: Comprehensive error handling for missing dependencies, API failures, S3 access issues, and file processing errors
- **Security**: Path validation prevents directory traversal attacks
- **Logging**: INFO level logging with timestamps for processing visibility
- **Caching**: Existing transcription and audio segment files are reused to avoid reprocessing

## Environment Configuration

The application uses environment variables for configuration (see `.env.example`):

```bash
OPENAI_API_KEY=your-api-key-here         # Required: OpenAI API access
OPENAI_BASE_URL=https://api.openai.com/v1 # Optional: Custom API endpoint
OPENAI_WHISPER_MODEL=whisper-1           # Transcription model
OPENAI_SUMMARY_MODEL=gpt-4o              # Summarization model
PROMPT_FILE=summarization_prompt.md      # Custom prompt template

# AWS S3 configuration (optional, for S3 file downloads)
AWS_ACCESS_KEY_ID=your-aws-access-key-id       # Required for S3 access
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key # Required for S3 access
AWS_DEFAULT_REGION=us-east-1                   # Optional: AWS region
AWS_ENDPOINT_URL=http://localhost:9000          # Optional: Custom S3 endpoint (MinIO, etc.)
```

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Documentation Maintenance Rules
- **README Updates**: When making changes to README.md, ALWAYS update both the English README.md and Russian README.ru.md files simultaneously to keep them in sync.
- **CLAUDE.md Updates**: When making significant changes to the project architecture, dependencies, commands, or core functionality, ALWAYS update this CLAUDE.md file to reflect these changes so future Claude instances have accurate information.
- **Version Consistency**: Ensure all documentation reflects the current state of the project and its capabilities.
