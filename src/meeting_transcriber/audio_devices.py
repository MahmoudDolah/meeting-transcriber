from __future__ import annotations

import platform

from .backends import linux as _linux
from .backends import macos as _macos


def _backend():
    return _macos if platform.system() == "Darwin" else _linux


def get_default_mic() -> str:
    return _backend().get_default_mic()


def get_default_monitor_source(override_sink: str | None = None) -> str:
    return _backend().get_default_monitor_source(override_sink)


def list_all_sources() -> str:
    return _backend().list_all_sources()
