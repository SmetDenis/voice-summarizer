#!/usr/bin/env python3
"""
Voice Summarizer - Audio/Video Transcription Script

Splits audio/video files into segments of max 9.5 minutes and transcribes them using OpenAI API.
Saves transcriptions as markdown files organized by input filename.

Usage:
    # Install dependencies
    uv pip install -r requirements.txt

    # Set up environment variables
    cp .env.example .env
    # Edit .env with your OpenAI API key

    # Run transcription
    python transcribe_audio.py input/your-file.mp4
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import tempfile
from openai import OpenAI
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, openai_api_key=None, openai_base_url=None, openai_model=None, summarization_model=None):
        """Initialize transcriber with OpenAI API key, base URL, and models."""
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        base_url = openai_base_url or os.getenv('OPENAI_BASE_URL')
        self.model = openai_model or os.getenv('OPENAI_WHISPER_MODEL', 'whisper-1')
        self.summarization_model = summarization_model or os.getenv('OPENAI_SUMMARY_MODEL', 'gpt-4o-mini')

        client_kwargs = {'api_key': api_key}
        if base_url:
            client_kwargs['base_url'] = base_url

        self.client = OpenAI(**client_kwargs)
        self.max_duration = 570  # 9.5 minutes in seconds

    def get_file_duration(self, file_path):
        """Get duration of audio/video file in seconds using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting file duration: {e}")
            raise
        except ValueError as e:
            logger.error(f"Error parsing duration: {e}")
            raise

    def _validate_path(self, path):
        """Validate that path is safe and doesn't contain path traversal attempts."""
        resolved_path = Path(path).resolve()
        # Ensure the path is within current working directory or a subdirectory
        try:
            resolved_path.relative_to(Path.cwd())
        except ValueError:
            raise ValueError(f"Unsafe path detected: {path}")
        return resolved_path

    def split_audio(self, input_file, output_dir):
        """Split audio/video file into segments of max 9.5 minutes."""
        input_path = Path(input_file)
        output_dir = self._validate_path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        duration = self.get_file_duration(input_file)
        logger.info(f"File duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

        segments = []
        segment_count = int(duration // self.max_duration) + (1 if duration % self.max_duration > 0 else 1)

        for i in range(segment_count):
            start_time = i * self.max_duration
            segment_duration = min(self.max_duration, duration - start_time)

            if segment_duration <= 0:
                break

            output_filename = f"{input_path.stem}_segment_{i+1:03d}.mp3"
            output_path = output_dir / output_filename

            cmd = [
                'ffmpeg', '-i', str(input_file),
                '-ss', str(start_time),
                '-t', str(segment_duration),
                '-acodec', 'libmp3lame',
                '-y',  # Overwrite output files
                str(output_path)
            ]

            logger.info(f"Creating segment {i+1}/{segment_count}: {output_filename}")
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                segments.append(output_path)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error creating segment {i+1}: {e}")
                raise

        return segments

    def transcribe_audio(self, audio_file):
        """Transcribe audio file using OpenAI API."""
        try:
            with open(audio_file, 'rb') as f:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    response_format="text"
                )
            return response
        except Exception as e:
            logger.error(f"Error transcribing {audio_file}: {e}")
            raise

    def save_transcription(self, transcription, segment_path, segments_dir):
        """Save transcription as markdown file in segments directory."""
        segment_name = segment_path.stem
        md_filename = f"{segment_name}.md"
        md_path = Path(segments_dir) / md_filename

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Transcription: {segment_name}\n\n")
            f.write(f"**Source file:** {segment_path.name}\n\n")
            f.write("## Transcription\n\n")
            f.write(transcription)

        logger.info(f"Saved transcription: {md_path}")
        return md_path

    def load_summarization_prompt(self, prompt_file="summarization_prompt.md"):
        """Load summarization prompt from file."""
        prompt_path = Path(prompt_file)
        if not prompt_path.exists():
            # Default prompt if file doesn't exist
            return "You are an expert in analyzing and summarizing transcribed audio content. Create a comprehensive summary of the provided transcription."

        return prompt_path.read_text(encoding='utf-8')

    def summarize_transcription(self, transcription_text, prompt_file="summarization_prompt.md"):
        """Summarize transcription using OpenAI API."""
        try:
            system_prompt = self.load_summarization_prompt(prompt_file)

            response = self.client.chat.completions.create(
                model=self.summarization_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcription_text}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error summarizing transcription: {e}")
            raise

    def process_file(self, input_file, output_dir="Output"):
        """Process audio/video file: split and transcribe."""
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Create subdirectory based on input filename
        file_subdir = input_path.name  # filename with extension
        output_path = self._validate_path(Path(output_dir) / file_subdir)
        segments_dir = output_path / "segments"

        logger.info(f"Processing file: {input_file}")
        logger.info(f"Output directory: {output_path}")

        # Split file into segments (audio files go to segments_dir)
        segments = self.split_audio(input_file, segments_dir)

        # Transcribe each segment
        transcription_files = []
        for i, segment_path in enumerate(segments, 1):
            logger.info(f"Transcribing segment {i}/{len(segments)}: {segment_path.name}")

            try:
                transcription = self.transcribe_audio(segment_path)
                md_path = self.save_transcription(transcription, segment_path, segments_dir)
                transcription_files.append(md_path)
            except Exception as e:
                logger.error(f"Failed to transcribe segment {segment_path}: {e}")
                continue

        # Create combined transcription in output directory
        combined_md = output_path / f"{input_path.stem}_combined.md"
        with open(combined_md, 'w', encoding='utf-8') as f:
            f.write(f"# Complete Transcription: {input_path.name}\n\n")
            f.write(f"**Source file:** {input_path.name}\n")
            f.write(f"**Total segments:** {len(segments)}\n")
            f.write(f"**Processing date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for i, md_file in enumerate(transcription_files, 1):
                if md_file.exists():
                    f.write(f"## Segment {i}\n\n")
                    content = md_file.read_text(encoding='utf-8')
                    # Extract just the transcription part
                    lines = content.split('\n')
                    transcription_start = False
                    for line in lines:
                        if line.strip() == "## Transcription":
                            transcription_start = True
                            continue
                        elif transcription_start and line.strip():
                            f.write(line + '\n')
                    f.write('\n\n')

        logger.info(f"Created combined transcription: {combined_md}")

        # Create summary if requested
        summary_md = None
        if hasattr(self, 'create_summary') and self.create_summary:
            try:
                logger.info("Creating summary of transcription...")
                combined_text = combined_md.read_text(encoding='utf-8')

                # Extract just the transcription content
                lines = combined_text.split('\n')
                transcription_content = []
                in_segment = False

                for line in lines:
                    if line.startswith('## Segment'):
                        in_segment = True
                        transcription_content.append(line)
                        continue
                    elif in_segment:
                        transcription_content.append(line)

                full_transcription = '\n'.join(transcription_content)

                summary = self.summarize_transcription(full_transcription, self.prompt_file)

                # Save summary
                summary_md = output_path / f"{input_path.stem}_summary.md"
                with open(summary_md, 'w', encoding='utf-8') as f:
                    f.write(f"# Summary: {input_path.name}\n\n")
                    f.write(f"**Source file:** {input_path.name}\n")
                    f.write(f"**Model used:** {self.summarization_model}\n")
                    f.write(f"**Processing date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(summary)

                logger.info(f"Created summary: {summary_md}")

            except Exception as e:
                logger.error(f"Failed to create summary: {e}")

        logger.info(f"Processing complete. Output files in: {output_path}")

        result = {
            'segments': segments,
            'transcriptions': transcription_files,
            'combined': combined_md
        }

        if summary_md:
            result['summary'] = summary_md

        return result


def main():
    parser = argparse.ArgumentParser(description='Voice Summarizer - Split and transcribe audio/video files using OpenAI')
    parser.add_argument('input_file', help='Path to input audio/video file (mp3, mp4, etc.)')
    parser.add_argument('-o', '--output', default='Output', help='Output directory (default: Output)')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--base-url', help='OpenAI base URL (or set OPENAI_BASE_URL env var)')
    parser.add_argument('--whisper-model', help='OpenAI Whisper model to use (or set OPENAI_WHISPER_MODEL env var, default: whisper-1)')
    parser.add_argument('--summary-model', help='Model for summarization (or set OPENAI_SUMMARY_MODEL env var, default: gpt-4o-mini)')
    parser.add_argument('--summarize', action='store_true', help='Create summary of transcription')
    parser.add_argument('--prompt-file', help='Path to summarization prompt file (or set PROMPT_FILE env var, default: summarization_prompt.md)')

    args = parser.parse_args()

    # Check for required dependencies
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("ffmpeg and ffprobe are required. Please install them first.")
        sys.exit(1)

    # Initialize transcriber
    try:
        transcriber = AudioTranscriber(args.api_key, args.base_url, args.whisper_model, args.summary_model)
        # Set summarization options
        transcriber.create_summary = args.summarize
        transcriber.prompt_file = args.prompt_file or os.getenv('PROMPT_FILE', 'summarization_prompt.md')
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        logger.error("Make sure you have set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Process file
    try:
        results = transcriber.process_file(args.input_file, args.output)
        logger.info("Successfully completed transcription!")
        return 0
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())