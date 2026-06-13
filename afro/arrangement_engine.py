"""
arrangement_engine.py
──────────────────
Specialist for high-level structure, scene sequencing, and energy builds.
Accepts optional MasterKG for cross-stage intelligence sharing.
"""

from workflow_tracker import tracker

class ArrangementEngine:
    def __init__(self, kg=None):
        self.kg = kg

    def suggest_optimal_sequence(self, scenes):
        """Builds a circular arrangement flow, KG-aware if enabled."""
        actual_sequence = []

        # If KG has emotion arc, prefer starting low and peaking
        if self.kg and self.kg.enabled:
            arc = self.kg.read("emotion_arc", [])
            if arc:
                sorted_indices = sorted(
                    range(len(scenes)),
                    key=lambda i: scenes[i].get("energy_percent", 50)
                )
                # Build an energy-arc sequence: low → build → peak → outro
                for step in range(8):
                    idx = sorted_indices[min(step, len(sorted_indices) - 1)]
                    actual_sequence.append(idx)
                tracker.log("ArrangementEngine", "KG Combinatoronics",
                            f"Energy-arc sequence from KG: {actual_sequence}")
                # Write back structural facts
                energies = [scenes[i].get("energy_percent", 50) for i in actual_sequence]
                self.kg.write("has_climax", any(e > 80 for e in energies), source="ArrangementEngine")
                has_outro = any(
                    s.get("name", "").lower() in ("outro", "fade", "close")
                    for s in scenes
                )
                self.kg.write("has_outro", has_outro, source="ArrangementEngine")
                self.kg.write("transition_density", len(scenes) / 8.0, source="ArrangementEngine")
                return actual_sequence

        # Default circular fallback
        for i in range(8):
            idx = i % len(scenes)
            actual_sequence.append(idx)
        tracker.log("ArrangementEngine", "Combinatoronics", f"Sequenced {len(actual_sequence)} parts from source blueprint.")
        return actual_sequence

    def get_energy_multiplier(self, scene_name, global_energy):
        """Scales velocity based on scene role."""
        low_energy_scenes = ["intro", "outro", "atmosphere", "reflection"]
        if any(x in scene_name.lower() for x in low_energy_scenes):
            return 0.7
        if "peak" in scene_name.lower() or "drop" in scene_name.lower():
            return 1.15
        return 1.0

    def get_transition_fill(self, current_scene, next_scene, bpm):
        fill_events = []
        curr_e = current_scene.get("energy_percent", 50)
        next_e = next_scene.get("energy_percent", 50)
        energy_jump = next_e - curr_e

        # KG can boost transition density based on reaction (e.g. "more euphoric")
        energy_bias = 0
        if self.kg and self.kg.enabled:
            energy_bias = self.kg.read("reaction_energy_bias", 0)

        if energy_jump + energy_bias > 20:
            tracker.log("ArrangementEngine", "Transition",
                        f"Injecting builds for {next_scene['name']} (+{energy_jump}% energy)")
            # More fills when energy jump is bigger
            n_fills = min(16, 8 + int((energy_jump + energy_bias) / 10))
            for i in range(n_fills):
                fill_events.append({
                    "pitch": 38,
                    "beat_offset": 3.0 + (i * (1.0 / n_fills)),
                    "velocity": min(127, 65 + (i * 4))
                })

        if curr_e > 80:
            fill_events.append({"pitch": 49, "beat_offset": 3.9, "velocity": 110})

        return fill_events
