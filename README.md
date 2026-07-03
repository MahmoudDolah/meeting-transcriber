# meeting-transcriber

Local, offline CLI that records mic + system audio during an online meeting
(Zoom, Google Meet, or anything else — it works at the OS audio layer, not
via any meeting app integration) and produces a timestamped, speaker-labeled
text transcript ready to hand to an LLM for notes/action items.

Transcription runs fully offline via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
(`small.en`, CPU, int8) — no audio ever leaves your machine.

## System requirements

Ubuntu 24.04+ (or derivatives) with PipeWire (the default audio server).

```bash
sudo apt install ffmpeg pipewire-pulse pulseaudio-utils
```

## Install

```bash
pipx install .
```

## Usage

```bash
# Start recording before your meeting; Ctrl+C when it ends
meeting-transcriber record --name "team-standup"

# If auto-detected audio sources are wrong, list them and override
meeting-transcriber list-devices
meeting-transcriber record --mic-source <name> --system-source <name>

# Re-run transcription on a previously recorded meeting
meeting-transcriber transcribe ~/meetings/20260703-143000-team-standup
```

Recordings and transcripts are saved to `~/meetings/<timestamp>[-<name>]/`:

```
mic.wav
system.wav
transcript.txt
```

`transcript.txt` looks like:

```
[00:00:04] Me: Hey, can you hear me okay?
[00:00:06] Others: Yeah, loud and clear.
```
