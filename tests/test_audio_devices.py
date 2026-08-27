from pathlib import Path

from meeting_transcriber.backends.linux import _parse_monitor_sources

FIXTURE = Path(__file__).parent / "fixtures" / "sample_pactl_output.txt"


def test_parse_monitor_sources_finds_real_monitors():
    listing = FIXTURE.read_text()
    monitors = _parse_monitor_sources(listing)

    assert "alsa_output.usb-Generic_USB_Audio_Device-00.analog-stereo.monitor" in monitors
    assert "alsa_output.pci-0000_09_00.1.hdmi-stereo.monitor" in monitors


def test_parse_monitor_sources_excludes_non_monitor_sources():
    listing = FIXTURE.read_text()
    monitors = _parse_monitor_sources(listing)

    assert "alsa_input.usb-HD_Web_Camera_HD_Web_Camera_Ucamera001-02.mono-fallback" not in monitors


def test_parse_monitor_sources_empty_listing():
    assert _parse_monitor_sources("") == []
