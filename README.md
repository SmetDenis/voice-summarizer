# Voice Summarizer

CLI Tool for automatic transcription of audio and video files with the ability to create text summaries. Uses OpenAI API for media file processing.

[🇷🇺 Русская версия](README_RU.md)

## System Requirements

- Python 3.12 or higher
- `uv` dependency manager
- Installed system utilities: `ffmpeg` and `ffprobe`
- Active OpenAI API key

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
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_WHISPER_MODEL=whisper-1
OPENAI_SUMMARY_MODEL=gpt-4o-mini
```

## Project Structure

```
voice/
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
# Transcribing a single file
python main.py input/recording.mp4

# Specifying custom output directory
python main.py input/recording.mp4 -o custom_output
```

### Transcription with Summarization

```bash
# Transcription with automatic summary creation
python main.py input/recording.mp4 --summarize

# Using custom prompt for summarization
python main.py input/recording.mp4 --summarize --prompt-file custom_prompt.md
```

### Model Configuration

```bash
# Specifying specific Whisper model
python main.py input/recording.mp4 --whisper-model whisper-1

# Specifying summarization model
python main.py input/recording.mp4 --summarize --summary-model gpt-4

# Full configuration with custom parameters
python main.py input/recording.mp4 \
    --whisper-model whisper-1 \
    --summarize \
    --summary-model gpt-4 \
    --prompt-file my_prompt.md \
    --api-key YOUR_API_KEY \
    --base-url https://custom-endpoint.com/v1
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
docker-compose run voice-summarizer input/your-recording.mp4 --summarize
```

### Manual Docker Image Build

```bash
# Building the image
docker build -t voice-summarizer .

# Running the container
docker run -v $(pwd)/input:/app/input:ro \
           -v $(pwd)/output:/app/output \
           -v $(pwd)/.env:/app/.env:ro \
           voice-summarizer input/your-file.mp4 --summarize
```

### Docker Compose Commands

```bash
# Show help
docker-compose run voice-summarizer --help

# Basic transcription
docker-compose run voice-summarizer input/recording.mp4

# Transcription with summarization
docker-compose run voice-summarizer input/recording.mp4 --summarize

# Using custom model
docker-compose run voice-summarizer input/recording.mp4 \
    --whisper-model whisper-1 \
    --summarize \
    --summary-model gpt-4

# Development mode (interactive shell)
docker-compose run voice-summarizer-dev
```

### Docker Version Advantages

- ✅ **Environment isolation**: All dependencies packaged in container
- ✅ **Easy installation**: No need to install Python and ffmpeg on host system
- ✅ **Reproducibility**: Consistent behavior across any platform
- ✅ **Security**: Process isolated from main system

### Docker Requirements

- Docker version 20.10 or higher
- Docker Compose version 2.0 or higher
- Minimum 2GB free space for the image

## Command Line Parameters

| Parameter | Description |
|-----------|-------------|
| `input_file` | Path to input audio/video file |
| `-o, --output` | Directory for saving results (default: Output) |
| `--api-key` | OpenAI API key (alternative to OPENAI_API_KEY variable) |
| `--base-url` | Base URL for OpenAI API (alternative to OPENAI_BASE_URL variable) |
| `--whisper-model` | Whisper model for transcription (default: whisper-1) |
| `--summary-model` | Model for summary creation (default: gpt-4o-mini) |
| `--summarize` | Enable text summary creation |
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
- Process logging with timestamps
- API and file operation error handling

## Creating Custom Prompts

To create your own summarization prompt:

1. Copy the `summarization_prompt.md` file
2. Modify the content according to requirements
3. The prompt is used as a system message, transcription text is passed separately
4. Specify the file path via the `--prompt-file` parameter or `PROMPT_FILE` environment variable

## Troubleshooting

### "ffmpeg not found" Error
Make sure ffmpeg is installed and available in the system PATH.

### API Authentication Error
Check the correctness of the OpenAI API key in the `.env` file.

### File Processing Errors
Ensure that the input file exists and is readable.

### API Limit Exceeded
Check that you have sufficient funds in your OpenAI account.

## License

The project is distributed without usage restrictions.
