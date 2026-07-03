from __future__ import annotations

from dataclasses import dataclass

from .transcriber import Segment


@dataclass
class Line:
    time: float  # absolute seconds from recording start
    speaker: str  # "Me" | "Others"
    text: str


def merge_transcripts(
    mic_segments: list[Segment],
    mic_offset: float,
    system_segments: list[Segment],
    system_offset: float,
) -> list[Line]:
    lines = [
        Line(time=seg.start + mic_offset, speaker="Me", text=seg.text) for seg in mic_segments
    ] + [
        Line(time=seg.start + system_offset, speaker="Others", text=seg.text)
        for seg in system_segments
    ]
    # Stable sort: mic entries were appended first, so exact-tie timestamps
    # resolve to "Me" first, deterministically.
    lines.sort(key=lambda line: line.time)
    return lines
