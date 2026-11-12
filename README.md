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
pipx install git+https://github.com/MahmoudDolah/meeting-transcriber
```

Or from a local clone:

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

Recordings and transcripts are saved to `~/meetings/<timestamp>[-<name>]/` by default. To save
them somewhere else, pass `-o` / `--output-dir`, or set `MEETING_TRANSCRIBER_OUTPUT_DIR` (e.g. in
your shell profile) to change the default; the flag takes precedence over the variable:

```bash
meeting-transcriber record --name "team-standup" -o ~/Documents/meeting-notes

export MEETING_TRANSCRIBER_OUTPUT_DIR=~/Documents/meeting-notes
meeting-transcriber record --name "team-standup"
```

Each meeting directory contains:

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

## License

[Apache 2.0](LICENSE)
