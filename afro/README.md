# Amapiano Beat Pipeline
**Gemini → Python MIDI Engine → FluidSynth → Mastered WAV/MP3**

A fully automated beat-production pipeline. Describe a beat in plain English,
and the system generates a production-ready audio file.

---

## Architecture

```
Prompt
  ↓
01_gemini_composer.py   — Gemini API → structured JSON blueprint
  ↓
02_midi_engine.py       — Music theory + pretty_midi → .mid files
  ↓                          piano.mid | bass.mid | drums.mid
03_render_audio.py      — FluidSynth + SF2 soundfont → .wav stems
  ↓                          piano.wav | bass.wav | drums.wav | stems_mix.wav
04_master.py            — DSP chain (HPF → EQ → Compress → Limit) → MASTER.wav/mp3
```

---

## Quick Start

### 1. Install dependencies

```bash
# Python libraries
pip install pretty_midi mido google-generativeai python-dotenv numpy scipy

# Optional for MP3 export
pip install pydub

# FluidSynth (audio renderer)
sudo apt install fluidsynth fluid-soundfont-gm   # Ubuntu/Debian
brew install fluidsynth                           # macOS
```

### 2. Set your Gemini API key

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```
Get a free key at https://aistudio.google.com/app/apikey

### 3. Run the full pipeline

```bash
python run_pipeline.py
```

Custom prompt:
```bash
python run_pipeline.py --prompt "Deep Afrohouse at 124 BPM in D minor, hypnotic"
```

---

## Running Steps Individually

```bash
# Step 1 — Generate blueprint
python 01_gemini_composer.py --prompt "Soulful Amapiano 112 BPM A minor"

# Step 2 — Generate MIDI files
python 02_midi_engine.py --blueprint blueprint.json --outdir output/

# Step 3 — Render to WAV
python 03_render_audio.py --outdir output/ --sf2 soundfonts/FluidR3_GM.sf2

# Step 4 — Master
python 04_master.py --input output/stems_mix.wav --lufs -14
```

---

## CLI Options

### run_pipeline.py
| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | built-in Amapiano prompt | Beat description in plain English |
| `--blueprint` | `blueprint.json` | Blueprint JSON path |
| `--outdir` | `output/` | Output directory |
| `--sf2` | auto-detect | Path to .sf2 SoundFont |
| `--lufs` | `-14.0` | Target loudness (streaming standard) |
| `--samplerate` | `44100` | Audio sample rate |
| `--skip-gemini` | off | Use existing blueprint (no API call) |
| `--skip-render` | off | Stop after MIDI generation |
| `--api-key` | env var | Gemini API key override |

---

## Output Files

| File | Description |
|------|-------------|
| `blueprint.json` | Gemini music blueprint |
| `output/piano.mid` | Piano chords + melody MIDI |
| `output/bass.mid` | Bassline MIDI |
| `output/drums.mid` | Drum pattern MIDI |
| `output/full_mix.mid` | All tracks combined MIDI |
| `output/piano.wav` | Rendered piano audio |
| `output/bass.wav` | Rendered bass audio |
| `output/drums.wav` | Rendered drums audio |
| `output/stems_mix.wav` | Mixed stems (pre-master) |
| `output/MASTER.wav` | **Final mastered beat (WAV)** |
| `output/MASTER.mp3` | **Final mastered beat (MP3)** |

---

## Upgrading the Pipeline

### Better soundfonts
- **Salamander Grand Piano** — https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html
- **GeneralUser GS** — https://schristiancollins.com/generaluser.php
- **FluidR3 GM** — ships with Ubuntu (`apt install fluid-soundfont-gm`)

### Swap Gemini for another LLM
In `01_gemini_composer.py`, replace the `genai` call with any provider that
returns JSON. The blueprint schema is fully documented in `SYSTEM_INSTRUCTION`.

### Add VST rendering
Replace the FluidSynth call in `03_render_audio.py` with a DAW headless render
(REAPER via ReaScript, or Bitwig's headless CLI) for professional-grade sounds.

---

## Blueprint JSON Schema

```json
{
  "genre": "Amapiano",
  "bpm": 112,
  "key": "A Minor",
  "time_signature": [4, 4],
  "structure": ["intro", "verse", "drop", "breakdown", "drop", "outro"],
  "chords": [["Am7", 4], ["Fmaj7", 4], ["Cmaj7", 4], ["G7", 4]],
  "piano": { "style": "soulful", "velocity": 88, "voicing": "open" },
  "bassline": [["A1", 1], ["A1", 1], ["E2", 1], ["G2", 1]],
  "bass": { "style": "log_drum", "octave": 2 },
  "drums": {
    "kick_pattern":    [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,1],
    "snare_pattern":   [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    "hihat_pattern":   [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
    "open_hat_pattern":[0,0,0,0, 0,0,1,0, 0,0,0,0, 0,0,1,0],
    "perc_pattern":    [0,1,0,1, 0,1,0,1, 0,1,0,1, 0,1,0,0],
    "swing": 56
  },
  "melody": {
    "notes": [["A5", 0.5], ["C5", 0.5], ["E5", 1.0]],
    "style": "call_and_response"
  },
  "fx": { "reverb_room_size": 0.4, "delay_beats": 0.25, "filter_cutoff_hz": 8000 }
}
```