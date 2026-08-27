# meeting-transcriber

Local, offline CLI that records mic + system audio during an online meeting
(Zoom, Google Meet, or anything else — it works at the OS audio layer, not
via any meeting app integration) and produces a timestamped, speaker-labeled
text transcript ready to hand to an LLM for notes/action items.

Transcription runs fully offline via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
(`small.en`, CPU, int8) — no audio ever leaves your machine.

## System requirements

### Ubuntu (24.04+, or derivatives, with PipeWire)

```bash
sudo apt install ffmpeg pipewire-pulse pulseaudio-utils
```

### macOS (Sonoma+)

System-audio capture needs a virtual loopback driver — macOS/CoreAudio has no built-in
"monitor" source the way PipeWire does — plus a one-time setup so audio still plays out loud
while it's also being captured.

```bash
brew install ffmpeg blackhole-2ch
```

1. Open **Audio MIDI Setup.app** (Spotlight search for it).
2. Click **+** in the bottom-left corner → **Create Multi-Output Device**.
3. Check both your normal output (e.g. "Built-in Output" / your speakers or headphones) and
   **BlackHole 2ch**.
4. In **System Settings → Sound → Output**, select this new Multi-Output Device.
5. When you first run `meeting-transcriber record`, macOS will prompt for microphone access
   for your terminal app — grant it (or check **System Settings → Privacy & Security →
   Microphone** if it doesn't prompt).

Re-run `meeting-transcriber list-devices` if `--mic-source`/`--system-source` overrides stop
working after plugging/unplugging an audio device — avfoundation device indices can shift.

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
