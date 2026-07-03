from meeting_transcriber.merge import merge_transcripts
from meeting_transcriber.transcriber import Segment


def test_merge_interleaves_by_absolute_time():
    mic = [Segment(0.0, 2.0, "Hey can you hear me"), Segment(10.0, 12.0, "Yes looks good")]
    system = [Segment(3.0, 5.0, "Sure I will share my screen"), Segment(6.0, 7.0, "Can everyone see it")]

    lines = merge_transcripts(mic, 0.0, system, 0.0)

    assert [(l.speaker, l.text) for l in lines] == [
        ("Me", "Hey can you hear me"),
        ("Others", "Sure I will share my screen"),
        ("Others", "Can everyone see it"),
        ("Me", "Yes looks good"),
    ]


def test_merge_applies_offsets():
    mic = [Segment(0.0, 1.0, "mic seg")]
    system = [Segment(0.0, 1.0, "system seg")]

    lines = merge_transcripts(mic, mic_offset=5.0, system_segments=system, system_offset=1.0)

    times = {l.speaker: l.time for l in lines}
    assert times["Me"] == 5.0
    assert times["Others"] == 1.0


def test_merge_ties_prefer_me():
    mic = [Segment(2.0, 3.0, "mic seg")]
    system = [Segment(2.0, 3.0, "system seg")]

    lines = merge_transcripts(mic, 0.0, system, 0.0)

    assert lines[0].speaker == "Me"
    assert lines[1].speaker == "Others"


def test_merge_empty_inputs():
    assert merge_transcripts([], 0.0, [], 0.0) == []
