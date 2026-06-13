# 🎹 Afro-house & Amapiano Beat Factory (Master KG Edition)
**Interactive AI Producer → Specialist Engines → Genetic Optimization → Mastered Audio**

A sophisticated, collaborative AI music production environment. This system goes beyond simple generation—it acts as a Digital Producer, Songwriter, and Mixing Engineer to create authentic Afro-house and Amapiano tracks.

---

## 🏗️ The "Glass Box" Architecture

The factory operates via a **Hybrid Generative Workflow**:
1.  **Creative Brain (Gemini)**: Transforms stories into multi-scene blueprints with melodic motifs and lyrical themes.
2.  **Specialist Engines**: 
    *   **Groove Engine**: Applies AI-informed humanization, micro-timing (behind-the-beat), and authentic 16th-note shaker DNA.
    *   **Arrangement Engine**: Manages energy curves and injects dynamic snare builds and transitions.
    *   **Vocal Guidance**: Generates call-and-response patterns and simple guide-melody MIDI tracks.
3.  **Genetic Optimizer (Optuna)**: A Bayesian search engine that runs parallel "musical experiments" to find the perfect BPM, swing, and percussion density.
4.  **Audio Pipeline**: Rendered via asset-aware **FluidSynth** and mastered through a professional DSP chain.

---

## ⚡ Key Features

- **Interactive CLI**: A visual command center powered by `rich` for producing, monitoring, and refining beats.
- **Combinatoronics Optimization**: Rearrange and "remix" existing beats to find the optimal structural flow.
- **God-Mode Manual Fallback**: 100% resilient to API failures. Use `MASTER_PROMPT.md` with any browser AI to generate asset-aware blueprints.
- **Contextual Reaction Editing**: Provide feedback (e.g., *"make the bass heavier"*) and let the system refine previous productions while remembering their context.
- **Workflow Evolution Tracker**: See exactly how the AI specialists refined your intent in real-time.
- **Vocal Songbook**: Automatic generation of scene-by-scene story beats and full lyrics.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pretty_midi mido google-generativeai python-dotenv numpy scipy rich optuna
sudo apt install fluidsynth fluid-soundfont-gm # Ubuntu
```

### 2. Launch the Factory
```bash
python3 beat_factory_cli.py
```

---

## 🛠️ Command Center (CLI)

| Option | Mode | Description |
|------|------|-------------|
| **[1] Produce New** | API | Describe a vibe and let Gemini build the draft. |
| **[2] Optimize** | Combinatoronics | Take a previous beat and mutate its structure/order. |
| **[3] History** | Database | View all past productions, their quality scores, and Hex IDs. |
| **[4] Manual Entry** | API-Zero | Step-by-step guide to use external AI with local assets. |
| **[5] React & Refine**| Memory | Select a beat, provide feedback, and iterate the production. |

---

## 🧬 Specialist Logic

### 🥁 The Groove Engine (`groove_engine.py`)
- **Humanization**: AI-scaled micro-timing jitter (up to 10ms).
- **Placement**: Global shifts (e.g., *behind_the_beat* for soulful Amapiano).
- **DNA**: Characteristic syncopated accents on the shaker and log-drum slides.

### 🌉 The Arrangement Engine (`arrangement_engine.py`)
- **Energy Scaling**: Automatic velocity multipliers based on scene role.
- **Dynamic Fills**: Injects crescendo snare rolls at energy-shift transitions.

### 🎤 Vocal Guidance (`vocal_guidance_engine.py`)
- **Call & Response**: Structural A-B-A-B patterns for hooks.
- **Guide Track**: Melodic MIDI reference (`vocal_guide.mid`) in the correct key.

---

## 📂 File Structure

- `beat_factory_cli.py`: The main interactive interface.
- `run_pipeline.py`: The core engine runner (supports `--manual`, `--optimize`, `--source-beat`).
- `01_gemini_composer.py`: API bridge for high-level creative composition.
- `02_midi_engine.py`: Orchestrator of the specialist agents.
- `factory_db.py`: Persistent SQLite storage of your musical lineage.
- `sound_registry.json`: Your library of SoundFonts and tags.
- `input/`: Target folder for manual AI blueprint pasting.
- `output/<HEX_ID>/`: Your finalized production assets (MIDI, Stems, Master MP3, Lyrics).

---

## 📐 Sovereignty: MASTER_PROMPT.md
The system automatically syncs your local assets into `MASTER_PROMPT.md`. If the API is down, simply copy this file to ChatGPT/Claude and paste the result into `input/manual_blueprint.json`. The factory will handle the rest with full asset awareness.
