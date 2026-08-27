from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..errors import (
    FFmpegNotFoundError,
    NoMicFoundError,
    NoMonitorSourceFoundError,
    PactlNotFoundError,
)

FFMPEG_COMMON = ["-hide_banner", "-loglevel", "error", "-nostdin"]


def _pactl(*args: str) -> str:
    try:
        result = subprocess.run(
            ["pactl", *args], capture_output=True, text=True, timeout=5, check=True
        )
    except FileNotFoundError as e:
        raise PactlNotFoundError(
            "`pactl` not found. Install it with: sudo apt install pulseaudio-utils"
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"pactl {' '.join(args)} failed: {e.stderr}") from e
    return result.stdout.strip()


def get_default_mic() -> str:
    source = _pactl("get-default-source")
    if not source:
        raise NoMicFoundError("Could not determine default microphone via pactl.")
    return source


def get_default_monitor_source(override_sink: str | None = None) -> str:
    sink = override_sink or _pactl("get-default-sink")
    candidate = f"{sink}.monitor"
    listing = _pactl("list", "sources")
    if candidate in listing:
        return candidate
    # Fallback: scan for *any* real monitor source ("Monitor of Sink" != n/a)
    monitors = _parse_monitor_sources(listing)
    if not monitors:
        raise NoMonitorSourceFoundError(
            "No system-audio monitor source found. Run "
            "`meeting-transcriber list-devices` and pass --system-source explicitly."
        )
    return monitors[0]


def _parse_monitor_sources(listing: str) -> list[str]:
    names, current = [], None
    for line in listing.splitlines():
        line = line.strip()
        if line.startswith("Name:"):
            current = line.split("Name:", 1)[1].strip()
        elif line.startswith("Monitor of Sink:") and current:
            if "n/a" not in line:
                names.append(current)
    return names


def list_all_sources() -> str:
    return _pactl("list", "short", "sources")


def ensure_capture_ready() -> None:
    if shutil.which("ffmpeg") is None:
        raise FFmpegNotFoundError("ffmpeg not found. Install it with: sudo apt install ffmpeg")


def build_record_cmd(source: str, out_path: Path) -> list[str]:
    return [
        "ffmpeg",
        *FFMPEG_COMMON,
        "-f", "pulse",
        "-i", source,
        "-ac", "1",
        "-ar", "16000",
        "-y", str(out_path),
    ]
