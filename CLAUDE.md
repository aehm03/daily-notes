# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a daily notes CLI application that records audio, transcribes it using Whisper, and formats it into structured markdown notes using Google's Gemini AI model. The notes are automatically appended to daily journal files in a Logseq-compatible format.

## Architecture

- **CLI Entry Point**: `daily_notes/cli.py` contains the main Typer application
- **Command**: Single `note` command that handles the complete workflow
- **Dependencies**: Uses `hns` for audio recording/transcription, `pydantic-ai` for AI formatting, and `typer` for CLI
- **Output**: Writes formatted notes to `~/Documents/logseq/journals/YYYY_MM_DD.md`

## Key Components

- **AudioRecorder**: Records audio at 16kHz mono
- **WhisperTranscriber**: Transcribes audio to text
- **note_agent**: Pydantic AI agent using Gemini 2.5 Flash Lite for formatting transcriptions into structured markdown

## Development Commands

Install dependencies:
```bash
uv sync --extra dev  # Includes pytest for testing
```

Run tests:
```bash
uv run pytest
```

Run the CLI:
```bash
uv run daily
```

Install as editable package:
```bash
uv pip install -e .
# Then use: daily
```

## Authentication

The application requires a Google API key to use Gemini for note formatting:

```bash
daily login  # Prompts for API key and stores it securely
```

API keys are stored in the user's app directory (`~/.config/daily-notes/config.json`).

## Important Notes

- The application expects a Logseq journal directory at `~/Documents/logseq/journals/`
- Notes are appended to daily files with 2-space indentation for Logseq compatibility
- Audio files are automatically cleaned up after transcription
- The AI agent is configured to always return a note and format TODO items clearly
- Configuration uses Pydantic models for data validation and serialization
