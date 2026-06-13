"""
vocal_guidance_engine.py
────────────────────────
Specialist for Call & Response patterns and Story-to-Text pairing.
"""

class VocalGuidanceEngine:
    def __init__(self):
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

    def generate_guide(self, scenes):
        """
        Pairs musical scenes with vocal guidance and story placeholders.
        """
        guide = []
        for s in scenes:
            scene_name = s['name'].lower()
            energy = s.get('energy_percent', 50)
            
            guidance = {
                "scene": s['name'],
                "bars": s['bars'],
                "pattern": "A-B-A-B (Call & Response)" if energy > 60 else "Atmospheric / Spoken Word",
                "story_placeholders": []
            }
            
            # Suggest patterns based on energy/role
            num_iterations = max(1, s['bars'] // 4)
            for i in range(num_iterations):
                if energy > 70:
                    guidance["story_placeholders"].append("[Call]: (High Energy Hook Line)")
                    guidance["story_placeholders"].append("[Response]: (Rhythmic Crowd Chant / Echo)")
                elif energy > 40:
                    guidance["story_placeholders"].append("[Call]: (Narrative Story Line)")
                    guidance["story_placeholders"].append("[Response]: (Melodic Motif / Ad-lib)")
                else:
                    guidance["story_placeholders"].append("[Vibe]: (Breath / Whispers / Atmospheric Text)")
            
            guide.append(guidance)
        return guide

    def get_guide_midi_notes(self, scene, key="A Minor"):
        """
        Returns simple MIDI guidance notes (e.g. root and fifth) 
        to help a singer stay in key during call/response.
        """
        # Logic to return basic guidance notes based on scene energy
        # (Simplified for now)
        return [("A4", 1.0), ("E5", 1.0)]
