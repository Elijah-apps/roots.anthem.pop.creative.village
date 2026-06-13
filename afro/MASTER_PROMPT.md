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
... (standard schema)

---

## 🔄 REFINEMENT MODE (Contextual Editing)
If the user provides a **Reaction** and a **Previous Blueprint**, your goal is to:
1.  Keep the core identity of the song (Key, Motifs).
2.  Modify specific parameters based on the reaction (e.g., if "bass too quiet", increase bass velocity or change `bass_cutoff`).
3.  Return the **Updated JSON** as the final output.

**Reaction:** [PASTE YOUR FEEDBACK HERE]
**Previous Blueprint:** [PASTE PREVIOUS JSON HERE]
