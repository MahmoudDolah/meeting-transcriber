from pathlib import Path

from meeting_transcriber.backends import linux, macos


def test_linux_build_record_cmd_uses_pulse():
    cmd = linux.build_record_cmd("alsa_input.foo", Path("/tmp/mic.wav"))

    assert cmd[0] == "ffmpeg"
    assert "-f" in cmd and cmd[cmd.index("-f") + 1] == "pulse"
    assert "-i" in cmd and cmd[cmd.index("-i") + 1] == "alsa_input.foo"
    assert cmd[-1] == "/tmp/mic.wav"
    assert "-ac" in cmd and cmd[cmd.index("-ac") + 1] == "1"
    assert "-ar" in cmd and cmd[cmd.index("-ar") + 1] == "16000"


def test_macos_build_record_cmd_uses_avfoundation():
    cmd = macos.build_record_cmd("1", Path("/tmp/system.wav"))

    assert cmd[0] == "ffmpeg"
    assert "-f" in cmd and cmd[cmd.index("-f") + 1] == "avfoundation"
    assert "-i" in cmd and cmd[cmd.index("-i") + 1] == ":1"
    assert cmd[-1] == "/tmp/system.wav"
    assert "-ac" in cmd and cmd[cmd.index("-ac") + 1] == "1"
    assert "-ar" in cmd and cmd[cmd.index("-ar") + 1] == "16000"
