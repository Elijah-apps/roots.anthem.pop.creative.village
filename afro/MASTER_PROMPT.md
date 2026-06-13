# Afro-house & Amapiano GOD-MODE PROMPT
Copy this to an external AI to generate a complete, optimized production package.

---

## 🎵 MISSION
You are the **Lead Producer & Songwriter**. Your goal is to generate a professional Afro-house/Amapiano package.
Request: **[PASTE VIBE HERE]**

## 📐 OUTPUT SCHEMA (RAW JSON ONLY)
Return a single JSON object. You must fill every field.

```json
{
  "title": "Song Title",
  "bpm": 110-126,
  "key": "A Minor, etc",
  "selected_soundfont_id": "std_gm_01",
  "groove_config": {
    "humanization_intensity": 0.8,
    "note_placement": "behind_the_beat",
    "percussion_complexity": 0.9
  },
  "manual_optimization": {
    "kick_density": 0.95,
    "perc_density": 0.8,
    "bass_cutoff": 250,
    "piano_reverb": 0.4,
    "target_lufs": -12.0
  },
  "global_motifs": {
    "piano_main": [["A4", 1.0]],
    "bass_main": [["A1", 2.0]],
    "vocal_hook": [["A5", 4.0]]
  },
  "scenes": [
    {
      "name": "Intro",
      "bars": 8,
      "energy_percent": 20,
      "arrangement": {"piano": "chords", "bass": "silent", "drums": "minimal"},
      "story_beats": "Atmospheric entrance...",
      "lyrics": "Full lyrics for this scene here..."
    }
  ],
  "drums": {
    "kick_pattern": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
    "snare_pattern": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    "hihat_pattern": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
    "perc_pattern": [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0]
  }
}
```

## 🎹 ASSETS
{
  "soundfonts": [
    {
      "id": "std_gm_01",
      "path": "/usr/share/sounds/sf2/FluidR3_GM.sf2",
      "name": "FluidR3 General MIDI",
      "tags": [
        "standard",
        "versatile",
        "gm"
      ],
      "description": "Standard high-quality GM soundfont"
    },
    {
      "id": "soundfonts_af289497",
      "path": "/usr/share/sounds/sf2/FluidR3_GM.sf2",
      "name": "FluidR3_GM",
      "tags": [
        "gm",
        "warm"
      ],
      "description": "Default Linux Soundfont"
    }
  ],
  "samples": []
}
