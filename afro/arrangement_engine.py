"""
arrangement_engine.py
──────────────────
Specialist for high-level structure, scene sequencing, and energy builds.
"""

from workflow_tracker import tracker

class ArrangementEngine:
    def __init__(self):
        pass

    def suggest_optimal_sequence(self, scenes):
        """Builds a circular arrangement flow."""
        actual_sequence = []
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
        
        if next_e > curr_e + 20:
            tracker.log("ArrangementEngine", "Transition", f"Injecting builds for {next_scene['name']} (+{next_e - curr_e}% energy)")
            for i in range(8): 
                fill_events.append({"pitch": 38, "beat_offset": 3.0 + (i * 0.125), "velocity": 70 + (i * 5)})
                
        if curr_e > 80:
            fill_events.append({"pitch": 49, "beat_offset": 3.9, "velocity": 110})
            
        return fill_events
