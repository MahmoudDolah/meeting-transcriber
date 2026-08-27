from pathlib import Path

from meeting_transcriber.backends.macos import BLACKHOLE_NAME_RE, parse_avfoundation_devices

FIXTURE = Path(__file__).parent / "fixtures" / "sample_avfoundation_devices.txt"


def test_parse_avfoundation_devices_finds_audio_only():
    devices = parse_avfoundation_devices(FIXTURE.read_text())

    assert (0, "MacBook Pro Microphone") in devices
    assert (1, "BlackHole 2ch") in devices
    assert (2, "External USB Microphone") in devices
    assert not any("Camera" in name for _, name in devices)
    assert not any("Capture screen" in name for _, name in devices)


def test_parse_avfoundation_devices_empty():
    assert parse_avfoundation_devices("") == []


def test_blackhole_name_re_matches_case_insensitively():
    assert BLACKHOLE_NAME_RE.search("BlackHole 2ch")
    assert BLACKHOLE_NAME_RE.search("blackhole 16ch")
    assert not BLACKHOLE_NAME_RE.search("MacBook Pro Microphone")
