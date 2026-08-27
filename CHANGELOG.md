# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-08-26

Initial stable release. This tag is the rollback point for the Linux-only baseline, kept as a
safety net while macOS support (see PR #1) is tested before merging.

### Added
- Record mic + system/loopback audio simultaneously on Ubuntu/PipeWire, via `pactl` device
  discovery and `ffmpeg -f pulse` capture.
- Fully offline transcription via faster-whisper (`small.en`, CPU, int8).
- Merge mic + system transcripts into a single timestamped, speaker-labeled text transcript.
- CI running pytest on Ubuntu and macOS.
