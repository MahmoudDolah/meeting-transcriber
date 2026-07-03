from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

MODEL_SIZE = "small.en"

_model: WhisperModel | None = None


@dataclass
class Segment:
    start: float
    end: float
    text: str


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe_file(path: Path) -> list[Segment]:
    model = _get_model()
    segments, _info = model.transcribe(str(path), vad_filter=True)
    return [Segment(s.start, s.end, s.text.strip()) for s in segments if s.text.strip()]
