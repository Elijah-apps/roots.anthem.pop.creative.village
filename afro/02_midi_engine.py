"""
02_midi_engine.py
─────────────────
STEP 2 OF 4 — Master KG Story-Driven MIDI Engine (Enhanced)

Integrates GrooveEngine for micro-timing and ArrangementEngine for flow.
Includes Vocal Guidance Engine for call & response.
"""

import argparse
import json
import random
import sys
from pathlib import Path

try:
    import pretty_midi
except ImportError:
    sys.exit("[ERROR] pretty_midi not installed.\nRun: pip install pretty_midi")

# ─── Specialized Engines ──────────────────────────────────────────────────────
from groove_engine import GrooveEngine
from arrangement_engine import ArrangementEngine
from vocal_guidance_engine import VocalGuidanceEngine

# ─── Constants & Theory ──────────────────────────────────────────────────────

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# GM drum map
KICK  = 36
RIMSHOT = 37
SNARE = 38
HIHAT_CLOSED = 42
HIHAT_OPEN   = 46
WOODBLOCK = 56
CONGA_HIGH = 63
CONGA_LOW = 64
PERC  = 75
SHAKER = 82 # GM Shaker


def note_name_to_midi(name: str, default_octave: int = 4) -> int:
    name = name.strip().replace("b", "#")
    if len(name) >= 2 and name[-1].isdigit():
        pitch_str = name[:-1]
        octave = int(name[-1])
    else:
        pitch_str = name
        octave = default_octave
    try:
        idx = NOTES.index(pitch_str)
    except ValueError: return 60
    return (octave + 1) * 12 + idx

# ─── Motif Evolution ───

def mutate_motif(motif: list, energy: int) -> list:
    mutated = []
    for note, dur in motif:
        if energy > 70 and dur >= 1.0 and random.random() > 0.6:
            mutated.append([note, dur/2])
            mutated.append([note, dur/2])
        else:
            mutated.append([note, dur])
    return mutated

# ─── Agents ───

class AgentState:
    def __init__(self, bpm: int, groove_config: dict = None):
        self.bpm = bpm
        self.sec_per_beat = 60.0 / bpm
        self.cursor_sec = 0.0
        self.groove = GrooveEngine(config=groove_config)
        self.arrangement = ArrangementEngine()
        self.vocal = VocalGuidanceEngine()

class PianoAgent:
    def __init__(self, instrument: pretty_midi.Instrument):
        self.inst = instrument
    def perform(self, scene: dict, global_motifs: dict, state: AgentState):
        role = scene["arrangement"].get("piano", "silent")
        if role == "silent":
            state.cursor_sec += (scene["bars"] * 4 * state.sec_per_beat)
            return
        energy = scene["energy_percent"]
        multiplier = state.arrangement.get_energy_multiplier(scene["name"], energy)
        motif = global_motifs.get("piano_main", [])
        current_motif = mutate_motif(motif, energy)
        start_time = state.cursor_sec
        l_cursor = 0.0
        while l_cursor < (scene["bars"] * 4):
            for note, dur in current_motif:
                if l_cursor >= (scene["bars"] * 4): break
                pitch = note_name_to_midi(note, 4)
                v = int((60 + int(energy * 0.6)) * multiplier)
                t_s, v_h = state.groove.apply_humanization(start_time + l_cursor * state.sec_per_beat, v)
                self.inst.notes.append(pretty_midi.Note(min(127, v_h), pitch, t_s, t_s + (dur * 0.9) * state.sec_per_beat))
                l_cursor += dur

class BassAgent:
    def __init__(self, instrument: pretty_midi.Instrument):
        self.inst = instrument
    def perform(self, scene: dict, global_motifs: dict, state: AgentState):
        role = scene["arrangement"].get("bass", "silent")
        if role == "silent": return
        energy = scene["energy_percent"]
        motif = global_motifs.get("bass_main", [])
        start_time = state.cursor_sec
        l_cursor = 0.0
        while l_cursor < (scene["bars"] * 4):
            for note, dur in motif:
                if l_cursor >= (scene["bars"] * 4): break
                pitch = note_name_to_midi(note, 2)
                t_s, v_h = state.groove.apply_humanization(start_time + l_cursor * state.sec_per_beat, 80 + int(energy * 0.4))
                self.inst.notes.append(pretty_midi.Note(min(127, v_h), pitch, t_s, t_s + (dur * 0.8) * state.sec_per_beat))
                l_cursor += dur

class DrumAgent:
    def __init__(self, drum_inst: pretty_midi.Instrument, shaker_inst: pretty_midi.Instrument):
        self.drums = drum_inst
        self.shaker = shaker_inst
    def perform(self, scene: dict, drum_cfg: dict, state: AgentState, swing: float = 0.5, next_scene: dict = None):
        role = scene["arrangement"].get("drums", "silent")
        if role == "silent": return
        bars = scene["bars"]
        energy = scene.get("energy_percent", 50)
        
        # 1. Shakers (Style-driven from GrooveEngine)
        for s in state.groove.get_shaker_pattern(bars, state.bpm):
            self.shaker.notes.append(pretty_midi.Note(
                velocity=s["velocity"],
                pitch=s["pitch"],
                start=state.cursor_sec + s["time"],
                end=state.cursor_sec + s["time"] + 0.05
            ))
            
        # 2. Main Drum & Hihat Patterns
        kick_p = drum_cfg.get("kick_pattern", [0]*16)
        snare_p = drum_cfg.get("snare_pattern", [0]*16)
        perc_p = drum_cfg.get("perc_pattern", [0]*16)
        
        for bar in range(bars):
            bar_s = state.cursor_sec + (bar * 4 * state.sec_per_beat)
            for step in range(16):
                # Apply swing to off-beats
                beat_off = step * 0.25 if step % 2 == 0 else (step - 1) * 0.25 + (0.5 * swing)
                t = bar_s + beat_off * state.sec_per_beat
                
                # Kick
                if kick_p[step]:
                    self.drums.notes.append(pretty_midi.Note(110, KICK, t, t + 0.05))
                    
                # Active elements (energy based)
                if energy > 30:
                    if snare_p[step]:
                        self.drums.notes.append(pretty_midi.Note(100, SNARE, t, t + 0.05))
                    if perc_p[step]:
                        self.drums.notes.append(pretty_midi.Note(90, PERC, t, t + 0.05))
                        
                # Dynamic Hi-hat interaction (Classic House off-beat open hat)
                if energy > 40:
                    if step in [4, 12]: # Off-beats (beat 2 and 4 off-beat)
                        self.drums.notes.append(pretty_midi.Note(82, HIHAT_OPEN, t, t + 0.15 * state.sec_per_beat))
                    elif step % 2 == 0 and not kick_p[step] and random.random() > 0.4:
                        self.drums.notes.append(pretty_midi.Note(65, HIHAT_CLOSED, t, t + 0.05))
                        
                # Dynamic Triplet Rimshot Rolls in high energy parts
                if energy > 70 and role == "full":
                    # Play rolls on the last beat (steps 12-15) of every second bar
                    if (bar % 2 == 1) and step in [12, 13, 14, 15]:
                        v_roll = int(80 + (step - 12) * 12)
                        t_double = t + 0.12 * state.sec_per_beat
                        # Double hit roll
                        self.drums.notes.append(pretty_midi.Note(v_roll, RIMSHOT, t, t + 0.04))
                        self.drums.notes.append(pretty_midi.Note(max(1, v_roll - 20), RIMSHOT, t_double, t_double + 0.04))
                        
        # 3. Conversational Polyrhythmic Percussion Layer
        if energy > 35:
            for p_event in state.groove.get_amapiano_perc_pattern(bars, state.bpm):
                self.drums.notes.append(pretty_midi.Note(
                    velocity=p_event["velocity"],
                    pitch=p_event["pitch"],
                    start=state.cursor_sec + p_event["time"],
                    end=state.cursor_sec + p_event["time"] + 0.05
                ))

        # 4. Arrangement transition fills
        if next_scene:
            last_bar_s = state.cursor_sec + (bars - 1) * 4 * state.sec_per_beat
            for f in state.arrangement.get_transition_fill(scene, next_scene, state.bpm):
                self.drums.notes.append(pretty_midi.Note(
                    velocity=f["velocity"],
                    pitch=f["pitch"],
                    start=last_bar_s + f["beat_offset"] * state.sec_per_beat,
                    end=last_bar_s + f["beat_offset"] * state.sec_per_beat + 0.05
                ))


class VocalGuideAgent:
    """Creates a melodic guide for Call & Response sections."""
    def __init__(self, instrument: pretty_midi.Instrument):
        self.inst = instrument
    def perform(self, scene: dict, state: AgentState):
        energy = scene.get("energy_percent", 50)
        if energy < 40: return # Only guide active sections
        
        notes = state.vocal.get_guide_midi_notes(scene)
        start_time = state.cursor_sec
        # Add simple guide notes every 2 bars
        for bar in range(0, scene["bars"], 2):
            t = start_time + (bar * 4 * state.sec_per_beat)
            for n_name, dur in notes:
                pitch = note_name_to_midi(n_name, 5)
                self.inst.notes.append(pretty_midi.Note(64, pitch, t, t + dur * state.sec_per_beat))
                t += (dur * state.sec_per_beat)

class LogDrumAgent:
    """Creates the signature syncopated Amapiano log drum track with rolls and slides."""
    def __init__(self, instrument: pretty_midi.Instrument):
        self.inst = instrument
    def perform(self, scene: dict, global_motifs: dict, state: AgentState):
        role = scene["arrangement"].get("bass", "silent")
        if role == "silent": return
        energy = scene["energy_percent"]
        if energy < 35: return # Skip atmospheric intro/outro
        
        motif = global_motifs.get("bass_main", [])
        start_time = state.cursor_sec
        l_cursor = 0.0
        
        temp_notes = []
        while l_cursor < (scene["bars"] * 4):
            for note, dur in motif:
                if l_cursor >= (scene["bars"] * 4): break
                pitch = note_name_to_midi(note, 2) # Low register
                
                # Check for rapid tremolo rolls in high energy parts
                if energy > 70 and random.random() > 0.7:
                    # 4 quick 16th notes
                    roll_vel = int(95 * state.arrangement.get_energy_multiplier(scene["name"], energy))
                    for step in range(4):
                        t = start_time + (l_cursor + step * 0.25) * state.sec_per_beat
                        temp_notes.append(pretty_midi.Note(
                            velocity=min(127, roll_vel),
                            pitch=pitch,
                            start=t,
                            end=t + 0.18 * state.sec_per_beat
                        ))
                else:
                    # Standard syncopated pulsing log drum
                    t = start_time + l_cursor * state.sec_per_beat
                    if random.random() > 0.5:
                        t += 0.25 * state.sec_per_beat # Syncopated off-beat shift
                    v = int((90 + int(energy * 0.25)) * state.arrangement.get_energy_multiplier(scene["name"], energy))
                    temp_notes.append(pretty_midi.Note(
                        velocity=min(127, v),
                        pitch=pitch,
                        start=t,
                        end=t + (dur * 0.75) * state.sec_per_beat
                    ))
                l_cursor += dur
                
        # Refine with GrooveEngine slides and slides mutation
        refined = state.groove.apply_log_drum_dynamics(temp_notes)
        self.inst.notes.extend(refined)

# ─── Orchestrator ───

def generate_midi(blueprint: dict, outdir: Path, genome: dict = None):
    bpm = genome.get("bpm") if genome else blueprint.get("bpm", 124)
    swing = genome.get("swing") if genome else 0.56
    
    groove_cfg = dict(blueprint.get("groove_config", {}))
    if genome:
        if "shaker_style" in genome:
            groove_cfg["shaker_style"] = genome["shaker_style"]
        if "perc_syncopation_level" in genome:
            groove_cfg["percussion_complexity"] = genome["perc_syncopation_level"]
            
    state = AgentState(bpm, groove_config=groove_cfg)

    
    p_inst = pretty_midi.Instrument(0, name="Piano")
    b_inst = pretty_midi.Instrument(38, name="Bass")
    ld_inst = pretty_midi.Instrument(39, name="Log Drum") # Synth Bass 2
    d_inst = pretty_midi.Instrument(0, is_drum=True, name="Drums")
    s_inst = pretty_midi.Instrument(0, is_drum=True, name="Shaker")
    v_inst = pretty_midi.Instrument(53, name="Vocal Guide") # Voice Oohs
    
    agents = [
        PianoAgent(p_inst), 
        BassAgent(b_inst), 
        LogDrumAgent(ld_inst), 
        DrumAgent(d_inst, s_inst), 
        VocalGuideAgent(v_inst)
    ]
    scenes = blueprint.get("scenes", [])
    
    is_amapiano = bpm < 118
    
    for i, scene in enumerate(scenes):
        c_cursor = state.cursor_sec
        next_s = scenes[i+1] if i+1 < len(scenes) else None
        
        # We must call agents in a specific order but handle cursor manually
        agents[0].perform(scene, blueprint.get("global_motifs", {}), state)
        end_cursor = state.cursor_sec
        
        state.cursor_sec = c_cursor
        agents[1].perform(scene, blueprint.get("global_motifs", {}), state)
        if is_amapiano:
            agents[2].perform(scene, blueprint.get("global_motifs", {}), state)
        agents[3].perform(scene, blueprint.get("drums", {}), state, swing, next_s)
        agents[4].perform(scene, state)
        
        state.cursor_sec = end_cursor

    outdir.mkdir(parents=True, exist_ok=True)
    
    tracks = {
        "piano.mid": [p_inst], 
        "bass.mid": [b_inst], 
        "drums.mid": [d_inst, s_inst], 
        "vocal_guide.mid": [v_inst],
    }
    if is_amapiano:
        tracks["log_drum.mid"] = [ld_inst]
        tracks["full_mix.mid"] = [p_inst, b_inst, ld_inst, d_inst, s_inst, v_inst]
    else:
        tracks["full_mix.mid"] = [p_inst, b_inst, d_inst, s_inst, v_inst]
        
    for name, insts in tracks.items():
        pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        pm.instruments.extend(insts)
        pm.write(str(outdir / name))
    return [outdir / k for k in tracks.keys()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", default="blueprint.json")
    parser.add_argument("--outdir", default="output")
    args = parser.parse_args()
    bp_path = Path(args.blueprint)
    if not bp_path.exists(): sys.exit(1)
    generate_midi(json.loads(bp_path.read_text()), Path(args.outdir))

if __name__ == "__main__":
    main()
