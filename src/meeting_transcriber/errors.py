class MeetingTranscriberError(Exception):
    """Base class for expected, user-facing failures."""


class PactlNotFoundError(MeetingTranscriberError):
    pass


class AVFoundationNotFoundError(MeetingTranscriberError):
    pass


class BlackHoleNotFoundError(MeetingTranscriberError):
    pass


class FFmpegNotFoundError(MeetingTranscriberError):
    pass


class NoMicFoundError(MeetingTranscriberError):
    pass


class NoMonitorSourceFoundError(MeetingTranscriberError):
    pass


class RecordingFailedError(MeetingTranscriberError):
    pass


class EmptyRecordingError(MeetingTranscriberError):
    pass
