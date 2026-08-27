from __future__ import annotations

import platform
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .backends import linux as _linux
from .backends import macos as _macos
from .errors import RecordingFailedError

# A finalized WAV has at least a 44-byte header; anything <= that is empty audio.
MIN_NONEMPTY_WAV_BYTES = 44


def _backend():
    return _macos if platform.system() == "Darwin" else _linux


@dataclass
class RecordingSession:
    mic_proc: subprocess.Popen
    system_proc: subprocess.Popen
    mic_path: Path
    system_path: Path
    mic_offset: float
    system_offset: float


def start_recording(mic_source: str, system_source: str, out_dir: Path) -> RecordingSession:
    backend = _backend()
    backend.ensure_capture_ready()
    out_dir.mkdir(parents=True, exist_ok=True)
    mic_path, system_path = out_dir / "mic.wav", out_dir / "system.wav"

    t_ref = time.monotonic()
    mic_proc = subprocess.Popen(
        backend.build_record_cmd(mic_source, mic_path),
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    t_mic = time.monotonic()
    system_proc = subprocess.Popen(
        backend.build_record_cmd(system_source, system_path),
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    t_sys = time.monotonic()

    return RecordingSession(
        mic_proc=mic_proc,
        system_proc=system_proc,
        mic_path=mic_path,
        system_path=system_path,
        mic_offset=t_mic - t_ref,
        system_offset=t_sys - t_ref,
    )


def stop_recording(session: RecordingSession) -> None:
    for proc in (session.mic_proc, session.system_proc):
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)

    errors: list[str] = []
    for proc, label in ((session.mic_proc, "mic"), (session.system_proc, "system")):
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            errors.append(f"{label} recording did not stop cleanly; audio file may be truncated.")

    if errors:
        raise RecordingFailedError(" ".join(errors))


def is_nonempty_recording(path: Path) -> bool:
    return path.exists() and path.stat().st_size > MIN_NONEMPTY_WAV_BYTES
