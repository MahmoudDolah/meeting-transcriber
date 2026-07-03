from __future__ import annotations

from pathlib import Path

from .merge import Line


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def write_transcript(lines: list[Line], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"[{format_timestamp(line.time)}] {line.speaker}: {line.text}\n")
