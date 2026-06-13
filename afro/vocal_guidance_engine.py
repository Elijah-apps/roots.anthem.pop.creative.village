"""
vocal_guidance_engine.py
────────────────────────
Specialist for Call & Response patterns and Story-to-Text pairing.
Accepts optional MasterKG for key, lyric tone, and reaction memory.
"""

class VocalGuidanceEngine:
    def __init__(self, kg=None):
        self.kg = kg
        self.patterns = {
            "chorus": [
                {"type": "call", "description": "Main Hook / Title Phrase", "bars": 2},
                {"type": "response", "description": "Harmonic Echo / Rhythmic Chant", "bars": 2}
            ],
            "verse": [
                {"type": "call", "description": "Narrative line 1", "bars": 2},
                {"type": "response", "description": "Instrumental pocket / Breath", "bars": 2}
            ]
        }
    _TONE_TEMPLATES = {
        "soulful":  {"high": "[Call]: (Soulful cry / Gospel shout)",
                     "mid":  "[Call]: (Heartfelt verse)",
                     "low":  "[Vibe]: (Whispered prayer)"},
        "euphoric": {"high": "[Call]: (Triumphant shout / Crowd rally)",
                     "mid":  "[Call]: (Celebration verse)",
                     "low":  "[Vibe]: (Rising anticipation)"},
        "dark":     {"high": "[Call]: (Intense chant / Warning)",
                     "mid":  "[Call]: (Brooding narrative)",
                     "low":  "[Vibe]: (Deep whisper)"},
        "bright":   {"high": "[Call]: (Joyful hook / Uplift)",
                     "mid":  "[Call]: (Upbeat dance call)",
                     "low":  "[Vibe]: (Playful hum)"},
    }

    def generate_guide(self, scenes):
        """
        Pairs musical scenes with vocal guidance and story placeholders.
        Reads lyric_tone and key from KG if available.
        """
        tone = self.kg.read("reaction_lyric_tone") if (self.kg and self.kg.enabled) else None
        tone_tmpl = self._TONE_TEMPLATES.get(tone, {})

        guide = []
        for s in scenes:
            energy = s.get('energy_percent', 50)
            pattern_label = "A-B-A-B (Call & Response)" if energy > 60 else "Atmospheric / Spoken Word"
            guidance = {
                "scene": s['name'],
                "bars": s['bars'],
                "pattern": pattern_label,
                "story_placeholders": []
            }
            num_iterations = max(1, s['bars'] // 4)
            for _ in range(num_iterations):
                if energy > 70:
                    guidance["story_placeholders"].append(
                        tone_tmpl.get("high", "[Call]: (High Energy Hook Line)"))
                    guidance["story_placeholders"].append("[Response]: (Rhythmic Crowd Chant / Echo)")
                elif energy > 40:
                    guidance["story_placeholders"].append(
                        tone_tmpl.get("mid", "[Call]: (Narrative Story Line)"))
                    guidance["story_placeholders"].append("[Response]: (Melodic Motif / Ad-lib)")
                else:
                    guidance["story_placeholders"].append(
                        tone_tmpl.get("low", "[Vibe]: (Breath / Whispers / Atmospheric Text)"))
            guide.append(guidance)

        if self.kg and self.kg.enabled:
            pat = "call_response" if any(s.get("energy_percent", 50) > 60 for s in scenes) else "atmospheric"
            self.kg.write("vocal_pattern", pat, source="VocalEngine")
            if tone:
                self.kg.write("lyric_tone_applied", tone, source="VocalEngine")

        return guide

    def get_guide_midi_notes(self, scene, key=None):
        """
        Returns simple MIDI guidance notes (root + fifth).
        Key is read from KG if available.
        """
        if key is None:
            key = (self.kg.read("key", "A Minor")
                   if (self.kg and self.kg.enabled) else "A Minor")
        key_guide_map = {
            "A Minor": [("A4", 1.0), ("E5", 1.0)],
            "C Major": [("C4", 1.0), ("G4", 1.0)],
            "D Minor": [("D4", 1.0), ("A4", 1.0)],
            "G Major": [("G4", 1.0), ("D5", 1.0)],
            "F Major": [("F4", 1.0), ("C5", 1.0)],
            "E Minor": [("E4", 1.0), ("B4", 1.0)],
        }
        return key_guide_map.get(key, [("A4", 1.0), ("E5", 1.0)])
