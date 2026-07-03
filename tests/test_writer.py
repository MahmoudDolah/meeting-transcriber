from pathlib import Path

from meeting_transcriber.merge import Line
from meeting_transcriber.writer import format_timestamp, write_transcript


def test_format_timestamp_basic():
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(192.4) == "00:03:12"


def test_format_timestamp_over_an_hour():
    assert format_timestamp(3661) == "01:01:01"


def test_write_transcript(tmp_path: Path):
    lines = [
        Line(time=4.0, speaker="Me", text="Hey can you hear me"),
        Line(time=6.0, speaker="Others", text="Yeah loud and clear"),
    ]
    out_path = tmp_path / "transcript.txt"

    write_transcript(lines, out_path)

    assert out_path.read_text() == (
        "[00:00:04] Me: Hey can you hear me\n"
        "[00:00:06] Others: Yeah loud and clear\n"
    )
