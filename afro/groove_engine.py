"""
groove_engine.py
────────────────
AI-Informed Specialist for micro-timing and rhythmic DNA.
"""

import random
import numpy as np
from workflow_tracker import tracker

class GrooveEngine:
    def __init__(self, style="amapiano", config=None):
        self.style = style
        self.config = config or {
            "humanization_intensity": 0.5,
            "swing_style": "straight",
            "percussion_complexity": 0.5,
            "note_placement": "on_grid"
        }
        tracker.log("GrooveEngine", "Initialization", f"AI Personality: {self.config.get('note_placement', 'N/A')}")

    def apply_humanization(self, start_time, velocity, amount_scale=1.0):
        intensity = self.config.get("humanization_intensity", 0.5)
        base_jitter = 0.01 * intensity * amount_scale
        
        placement = self.config.get("note_placement", "on_grid")
        offset = 0.0
        if placement == "behind_the_beat":
            offset = 0.015 * intensity 
        elif placement == "ahead_of_the_beat":
            offset = -0.01 * intensity 
            
        new_start = start_time + offset + random.uniform(-base_jitter, base_jitter)
        vel_jitter = 0.1 * intensity
        new_vel = int(velocity * random.uniform(1.0 - vel_jitter, 1.0 + vel_jitter))
        
        return new_start, min(127, max(1, new_vel))

    def get_shaker_pattern(self, bars, bpm):
        complexity = self.config.get("percussion_complexity", 0.5)
        tracker.log("GrooveEngine", "Rhythmic DNA", f"Generating shaker DNA (Complexity: {complexity:.2f})")
        
        sec_per_beat = 60.0 / bpm
        step_dur = sec_per_beat / 4.0
        pattern = []
        
        for step in range(bars * 16):
            if complexity < 0.3 and step % 2 == 1: continue
            is_accent = (step % 3 == 0)
            base_vel = 85 if is_accent else 45
            bar_pos = (step % 64) / 64.0
            swell = 1.0 + (0.2 * np.sin(bar_pos * np.pi))
            t = step * step_dur
            v = int(base_vel * swell)
            pattern.append({"time": t, "velocity": v, "pitch": 42})
        return pattern

    def apply_log_drum_dynamics(self, notes):
        intensity = self.config.get("humanization_intensity", 0.5)
        tracker.log("GrooveEngine", "Bass Refinement", f"Adding log-drum slides (Intensity: {intensity:.2f})")
        enhanced = []
        for n in notes:
            if n.duration > 0.5 and random.random() < (0.3 * intensity):
                slide_pitch = n.pitch - 12
                enhanced.append({"pitch": slide_pitch, "start": n.start - 0.05, "end": n.start, "velocity": int(n.velocity * 0.7)})
            enhanced.append({"pitch": n.pitch, "start": n.start, "end": n.end, "velocity": n.velocity})
        return enhanced
