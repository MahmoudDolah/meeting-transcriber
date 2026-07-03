from __future__ import annotations

import re
import sys
import time
from datetime import datetime
from pathlib import Path

import click

from . import audio_devices, recorder
from .errors import EmptyRecordingError, MeetingTranscriberError
from .merge import merge_transcripts
from .transcriber import transcribe_file
from .writer import write_transcript

DEFAULT_OUTPUT_DIR = Path.home() / "meetings"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def _meeting_dir(output_dir: Path, name: str | None) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if name:
        slug = _slugify(name)
        if slug:
            stamp = f"{stamp}-{slug}"
    return output_dir / stamp


def _transcribe_meeting(meeting_dir: Path, mic_offset: float = 0.0, system_offset: float = 0.0) -> Path:
    mic_path = meeting_dir / "mic.wav"
    system_path = meeting_dir / "system.wav"

    mic_segments = (
        transcribe_file(mic_path) if recorder.is_nonempty_recording(mic_path) else []
    )
    system_segments = (
        transcribe_file(system_path) if recorder.is_nonempty_recording(system_path) else []
    )

    if not mic_segments and not system_segments:
        raise EmptyRecordingError(
            f"No audio detected in {mic_path} or {system_path}; nothing to transcribe."
        )
    if not mic_segments:
        click.echo("Warning: no mic audio detected.", err=True)
    if not system_segments:
        click.echo("Warning: no system audio detected — check --system-source.", err=True)

    lines = merge_transcripts(mic_segments, mic_offset, system_segments, system_offset)
    transcript_path = meeting_dir / "transcript.txt"
    write_transcript(lines, transcript_path)
    return transcript_path


@click.group()
def main() -> None:
    """Record and transcribe online meetings, fully offline."""


@main.command()
@click.option("--name", default=None, help="Optional label for the meeting directory.")
@click.option("--mic-source", default=None, help="Override auto-detected mic source.")
@click.option("--system-source", default=None, help="Override auto-detected system-audio monitor source.")
@click.option(
    "-o", "--output-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    help="Base directory to save recordings/transcripts under.",
)
def record(name: str | None, mic_source: str | None, system_source: str | None, output_dir: Path) -> None:
    """Record mic + system audio; transcribe automatically on stop."""
    try:
        mic_source = mic_source or audio_devices.get_default_mic()
        system_source = system_source or audio_devices.get_default_monitor_source()
    except MeetingTranscriberError as e:
        raise click.ClickException(str(e))

    meeting_dir = _meeting_dir(output_dir, name)
    meeting_dir.mkdir(parents=True, exist_ok=True)

    try:
        session = recorder.start_recording(mic_source, system_source, meeting_dir)
    except MeetingTranscriberError as e:
        raise click.ClickException(str(e))

    click.echo(f"Recording to {meeting_dir}")
    click.echo("Recording... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        click.echo("\nStopping recording...")
        try:
            recorder.stop_recording(session)
        except MeetingTranscriberError as e:
            click.echo(f"Warning: {e}", err=True)

    click.echo("Transcribing (this may take a minute; downloads the model on first run)...")
    try:
        transcript_path = _transcribe_meeting(meeting_dir, session.mic_offset, session.system_offset)
    except KeyboardInterrupt:
        click.echo(
            "\nTranscription interrupted. Audio was saved — re-run:\n"
            f"  meeting-transcriber transcribe {meeting_dir}"
        )
        sys.exit(1)
    except MeetingTranscriberError as e:
        raise click.ClickException(str(e))

    click.echo(f"Saved transcript to {transcript_path}")


@main.command("list-devices")
def list_devices() -> None:
    """List available audio sources for --mic-source / --system-source overrides."""
    try:
        click.echo(audio_devices.list_all_sources())
        click.echo()
        click.echo(f"Auto-detected mic:    {audio_devices.get_default_mic()}")
        click.echo(f"Auto-detected system: {audio_devices.get_default_monitor_source()}")
    except MeetingTranscriberError as e:
        raise click.ClickException(str(e))


@main.command()
@click.argument("meeting_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def transcribe(meeting_dir: Path) -> None:
    """Re-run transcription on an already-recorded meeting directory."""
    click.echo("Transcribing...")
    try:
        transcript_path = _transcribe_meeting(meeting_dir)
    except MeetingTranscriberError as e:
        raise click.ClickException(str(e))
    click.echo(f"Saved transcript to {transcript_path}")
