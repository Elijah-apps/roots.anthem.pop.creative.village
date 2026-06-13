"""
groove_engine.py
────────────────
AI-Informed Specialist for micro-timing and rhythmic DNA.
Accepts optional MasterKG for cross-stage intelligence sharing.
"""

import random
import numpy as np
from workflow_tracker import tracker

class GrooveEngine:
    def __init__(self, style="amapiano", config=None, kg=None):
        self.style = style
        self.kg = kg

        # Base defaults
        base_config = {
            "humanization_intensity": 0.5,
            "swing_style": "straight",
            "percussion_complexity": 0.5,
            "note_placement": "on_grid"
        }

        # KG enrichment: genre-aware presets fill in any missing keys
        if kg and kg.enabled:
            kg_groove = kg.resolve_groove_config()
            if kg_groove:
                # KG presets are defaults; explicit config overrides them
                merged = {**kg_groove, **(config or {})}
                self.config = {**base_config, **merged}
                tracker.log("GrooveEngine", "KG Config",
                            f"Genre: {kg.read('genre')} → shaker: {self.config.get('shaker_style')} "
                            f"| placement: {self.config.get('note_placement')}")
            else:
                self.config = {**base_config, **(config or {})}
        else:
            self.config = {**base_config, **(config or {})}

        # Write chosen config back to KG so downstream stages can see it
        if kg and kg.enabled:
            kg.write("groove_shaker_style",   self.config.get("shaker_style"),   source="GrooveEngine")
            kg.write("groove_note_placement",  self.config.get("note_placement"), source="GrooveEngine")
            kg.write("groove_humanization",    self.config.get("humanization_intensity"), source="GrooveEngine")
            kg.write("groove_perc_complexity", self.config.get("percussion_complexity"),  source="GrooveEngine")

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
        style = self.config.get("shaker_style", "classic_shuffle")
        tracker.log("GrooveEngine", "Rhythmic DNA", f"Generating shaker DNA (Style: {style}, Complexity: {complexity:.2f})")
        
        sec_per_beat = 60.0 / bpm
        step_dur = sec_per_beat / 4.0
        pattern = []
        
        # Classic Amapiano Shuffle accents: steps 0, 3, 6, 8, 11, 14
        amapiano_accents = {0, 3, 6, 8, 11, 14}
        
        for bar in range(bars):
            for step_in_bar in range(16):
                step = bar * 16 + step_in_bar
                t = step * step_dur
                
                # Complexity gating
                if complexity < 0.35 and step_in_bar % 2 == 1:
                    continue
                    
                is_accent = False
                time_offset = 0.0
                
                if style == "classic_shuffle":
                    is_accent = step_in_bar in amapiano_accents
                elif style == "triplet_bounce":
                    is_accent = (step_in_bar % 3 == 0)
                    # Triplet shuffle offset
                    if step_in_bar % 3 == 2:
                        time_offset = step_dur * 0.08
                else: # straight_groove
                    is_accent = (step_in_bar % 4 == 0) or (step_in_bar % 4 == 2)
                
                base_vel = 90 if is_accent else 40
                bar_pos = (step % 64) / 64.0
                swell = 1.0 + (0.15 * np.sin(bar_pos * np.pi))
                v = int(base_vel * swell)
                v = int(v * random.uniform(0.9, 1.1))
                
                pattern.append({
                    "time": t + time_offset,
                    "velocity": min(127, max(1, v)),
                    "pitch": 82 # GM Shaker
                })
        return pattern

    def get_amapiano_perc_pattern(self, bars, bpm):
        complexity = self.config.get("percussion_complexity", 0.5)
        sec_per_beat = 60.0 / bpm
        step_dur = sec_per_beat / 4.0
        pattern = []
        
        # Authentic Conga / Rimshot polyrhythmic syncopations
        for bar in range(bars):
            bar_start = bar * 16 * step_dur
            
            # 1. Rimshots / cross-sticks
            rim_steps = [3, 7, 11, 14]
            if complexity > 0.6:
                rim_steps += [5, 9]
            for step in rim_steps:
                v = int(85 * random.uniform(0.85, 1.1))
                t = bar_start + step * step_dur
                pattern.append({"time": t, "velocity": v, "pitch": 37})
                
            # 2. Congas: conversational hand drums (Low Conga 64, High Conga 63)
            conga_steps = [(2, 64), (6, 63), (10, 64), (13, 63)]
            if complexity > 0.5:
                conga_steps += [(8, 64), (15, 63)]
            for step, pitch in conga_steps:
                v = int(75 * random.uniform(0.8, 1.15))
                t = bar_start + step * step_dur
                pattern.append({"time": t, "velocity": v, "pitch": pitch})
                
            # 3. Woodblock (56) accents
            wb_steps = [4, 12]
            if complexity > 0.7:
                wb_steps += [0, 8]
            for step in wb_steps:
                v = int(80 * random.uniform(0.85, 1.05))
                t = bar_start + step * step_dur
                pattern.append({"time": t, "velocity": v, "pitch": 56})
                
        return pattern


    def apply_log_drum_dynamics(self, notes):
        intensity = self.config.get("humanization_intensity", 0.5)
        tracker.log("GrooveEngine", "Bass Refinement", f"Adding log-drum slides (Intensity: {intensity:.2f})")
        import pretty_midi
        enhanced = []
        for n in notes:
            duration = n.end - n.start
            if duration > 0.5 and random.random() < (0.3 * intensity):
                slide_pitch = n.pitch - 12
                slide_start = max(0.0, n.start - 0.05)
                # Create a slide note transitioning into the main note
                enhanced.append(pretty_midi.Note(
                    velocity=min(127, max(1, int(n.velocity * 0.7))),
                    pitch=slide_pitch,
                    start=slide_start,
                    end=n.start
                ))
            enhanced.append(pretty_midi.Note(
                velocity=n.velocity,
                pitch=n.pitch,
                start=n.start,
                end=n.end
            ))
        return enhanced

