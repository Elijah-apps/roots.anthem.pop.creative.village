# Afro-house & Amapiano GOD-MODE PROMPT (Asset-Aware)
Copy this to an external AI to generate a complete production package.

---

## 🎵 MISSION
You are the **Lead Producer & Songwriter**. Your goal is to generate a professional Afro-house/Amapiano package.
Request: **[PASTE VIBE HERE]**

## 🎹 LOCAL ASSET REGISTRY (Use these IDs!)
Choose the most appropriate `selected_soundfont_id` from the list below based on their tags and descriptions. 
**DO NOT make up IDs. Only use what is listed here.**

{REGISTRY_JSON}

## 📐 OUTPUT SCHEMA (RAW JSON ONLY)
```json
{
  "title": "Song Title",
  "bpm": 113,
  "key": "A Minor",
  "selected_soundfont_id": "std_gm_01",
  "groove_config": {
    "humanization_intensity": 0.6,
    "swing_style": "swingy",
    "percussion_complexity": 0.7,
    "note_placement": "behind_the_beat"
  },
  "global_motifs": {
    "piano_main": [["A4", 1.0], ["C5", 1.0], ["E5", 0.5], ["A4", 1.5]],
    "bass_main": [["A1", 1.0], ["A1", 1.0], ["E2", 1.0], ["G2", 1.0]],
    "vocal_hook": [["E5", 2.0], ["D5", 1.0], ["C5", 1.0]]
  },
  "scenes": [
    {
      "name": "Intro",
      "energy_percent": 15,
      "bars": 8,
      "arrangement": {
        "piano": "chords",
        "bass": "silent",
        "drums": "silent"
      },
      "story_beats": "A slow build-up reflecting sunrise.",
      "lyrics": "Helela, helela khanya...\nLet there be light in the village..."
    }
  ],
  "drums": {
    "kick_pattern": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
    "snare_pattern": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
    "hihat_pattern": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
    "perc_pattern": [0,1,0,1, 0,1,0,1, 0,1,0,1, 0,1,0,0]
  }
}
```

---


## 🔄 REFINEMENT MODE (Contextual Editing)
If the user provides a **Reaction** and a **Previous Blueprint**, your goal is to:
1.  Keep the core identity of the song (Key, Motifs).
2.  Modify specific parameters based on the reaction (e.g., if "bass too quiet", increase bass velocity or change `bass_cutoff`).
3.  Return the **Updated JSON** as the final output.

**Reaction:** [PASTE YOUR FEEDBACK HERE]
**Previous Blueprint:** [PASTE PREVIOUS JSON HERE]
