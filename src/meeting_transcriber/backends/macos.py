from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from ..errors import (
    AVFoundationNotFoundError,
    BlackHoleNotFoundError,
    FFmpegNotFoundError,
    NoMicFoundError,
)

FFMPEG_COMMON = ["-hide_banner", "-loglevel", "error", "-nostdin"]

BLACKHOLE_NAME_RE = re.compile(r"blackhole", re.IGNORECASE)

_DEVICE_LINE_RE = re.compile(r"\[(\d+)\]\s+(.+)")


def _run_list_devices_raw() -> str:
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True, text=True, timeout=10,
    )
    return result.stderr


def parse_avfoundation_devices(stderr_text: str) -> list[tuple[int, str]]:
    devices: list[tuple[int, str]] = []
    in_audio_section = False
    for line in stderr_text.splitlines():
        if "AVFoundation video devices" in line:
            in_audio_section = False
            continue
        if "AVFoundation audio devices" in line:
            in_audio_section = True
            continue
        if not in_audio_section:
            continue
        match = _DEVICE_LINE_RE.search(line)
        if match:
            devices.append((int(match.group(1)), match.group(2).strip()))
    return devices


def list_avfoundation_audio_devices() -> list[tuple[int, str]]:
    return parse_avfoundation_devices(_run_list_devices_raw())


def _coreaudio_default_input_name() -> str | None:
    # Best-effort: pyobjc's CoreAudio bridging is fiddly and unverified here without
    # real macOS hardware to test against, so any failure just falls through to the
    # non-BlackHole heuristic in get_default_mic() rather than blocking recording.
    try:
        from CoreAudio import (
            AudioObjectGetPropertyData,
            AudioObjectPropertyAddress,
            kAudioHardwarePropertyDefaultInputDevice,
            kAudioObjectPropertyElementMaster,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectSystemObject,
            kAudioObjectPropertyName,
        )
    except ImportError:
        return None

    try:
        addr = AudioObjectPropertyAddress(
            kAudioHardwarePropertyDefaultInputDevice,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster,
        )
        _, _, device_id = AudioObjectGetPropertyData(
            kAudioObjectSystemObject, addr, 0, None, 4
        )
        name_addr = AudioObjectPropertyAddress(
            kAudioObjectPropertyName,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMaster,
        )
        _, _, name = AudioObjectGetPropertyData(device_id, name_addr, 0, None, 256)
        return str(name) if name else None
    except Exception:
        return None


def get_default_mic() -> str:
    devices = list_avfoundation_audio_devices()
    if not devices:
        raise NoMicFoundError(
            "No audio input devices found via ffmpeg avfoundation. Check System Settings > "
            "Privacy & Security > Microphone permissions for your terminal app."
        )

    default_name = _coreaudio_default_input_name()
    if default_name:
        for idx, name in devices:
            if name == default_name or default_name in name:
                return str(idx)

    for idx, name in devices:
        if not BLACKHOLE_NAME_RE.search(name):
            return str(idx)

    raise NoMicFoundError(
        "Could not auto-detect a default microphone; pass --mic-source explicitly. "
        "Run `meeting-transcriber list-devices` to see available indices."
    )


def get_default_monitor_source(override_sink: str | None = None) -> str:
    if override_sink:
        return override_sink
    devices = list_avfoundation_audio_devices()
    for idx, name in devices:
        if BLACKHOLE_NAME_RE.search(name):
            return str(idx)
    raise BlackHoleNotFoundError(
        "No BlackHole input device found. Install it with: brew install blackhole-2ch, then "
        "create a Multi-Output Device (Built-in Output + BlackHole 2ch) in Audio MIDI Setup.app "
        "and set it as your system output. See README for details."
    )


def list_all_sources() -> str:
    devices = list_avfoundation_audio_devices()
    return "\n".join(f"{idx}: {name}" for idx, name in devices)


def ensure_capture_ready() -> None:
    if shutil.which("ffmpeg") is None:
        raise FFmpegNotFoundError("ffmpeg not found. Install it with: brew install ffmpeg")
    if not list_avfoundation_audio_devices():
        raise AVFoundationNotFoundError(
            "No audio input devices found via ffmpeg avfoundation. Check System Settings > "
            "Privacy & Security > Microphone permissions for your terminal app."
        )


def build_record_cmd(source: str, out_path: Path) -> list[str]:
    return [
        "ffmpeg",
        *FFMPEG_COMMON,
        "-f", "avfoundation",
        "-i", f":{source}",
        "-ac", "1",
        "-ar", "16000",
        "-y", str(out_path),
    ]
