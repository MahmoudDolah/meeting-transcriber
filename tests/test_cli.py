from pathlib import Path

import pytest
from click.testing import CliRunner

from meeting_transcriber import cli
from meeting_transcriber.errors import MeetingTranscriberError


@pytest.fixture
def started_dirs(monkeypatch):
    """Stub out device detection and abort at start_recording, capturing the meeting dir."""
    dirs: list[Path] = []

    def fake_start_recording(mic_source, system_source, meeting_dir):
        dirs.append(meeting_dir)
        raise MeetingTranscriberError("stop here")

    monkeypatch.setattr(cli.audio_devices, "get_default_mic", lambda: "mic")
    monkeypatch.setattr(cli.audio_devices, "get_default_monitor_source", lambda: "monitor")
    monkeypatch.setattr(cli.recorder, "start_recording", fake_start_recording)
    monkeypatch.delenv(cli.OUTPUT_DIR_ENVVAR, raising=False)
    return dirs


def test_record_uses_output_dir_envvar(started_dirs, tmp_path):
    runner = CliRunner()
    runner.invoke(cli.main, ["record"], env={cli.OUTPUT_DIR_ENVVAR: str(tmp_path / "env")})

    assert started_dirs[0].parent == tmp_path / "env"


def test_record_output_dir_flag_overrides_envvar(started_dirs, tmp_path):
    runner = CliRunner()
    runner.invoke(
        cli.main,
        ["record", "-o", str(tmp_path / "flag")],
        env={cli.OUTPUT_DIR_ENVVAR: str(tmp_path / "env")},
    )

    assert started_dirs[0].parent == tmp_path / "flag"


def test_record_expands_tilde_in_output_dir(started_dirs, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    runner = CliRunner()
    runner.invoke(cli.main, ["record"], env={cli.OUTPUT_DIR_ENVVAR: "~/notes"})

    assert started_dirs[0].parent == tmp_path / "notes"
