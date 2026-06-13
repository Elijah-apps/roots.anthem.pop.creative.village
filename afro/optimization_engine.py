import optuna
import random
import numpy as np


def suggest_genome(trial: optuna.Trial, num_scenes: int = 0):
    """
    Defines the search space for a Beat Genome, now including 
    Combinatoronics (structural rearrangement) and Amapiano percussion.
    """
    genome = {
        # 1. Tempo & Swing
        "bpm": trial.suggest_int("bpm", 108, 126),
        "swing": trial.suggest_float("swing", 0.50, 0.70),
        
        # 2. Arrangement Structure (Combinatoronics)
        "scene_sequence": [
            trial.suggest_int(f"scene_idx_{i}", 0, max(0, num_scenes - 1))
            for i in range(max(num_scenes, 8))
        ] if num_scenes > 0 else [],
        
        # 3. Density & Evolution
        "kick_density": trial.suggest_float("kick_density", 0.5, 1.0),
        "perc_density": trial.suggest_float("perc_density", 0.3, 0.9),
        
        # 4. Amapiano Drum & Shaker parameters
        "shaker_style": trial.suggest_categorical("shaker_style", ["classic_shuffle", "triplet_bounce", "straight_groove"]),
        "perc_syncopation_level": trial.suggest_float("perc_syncopation_level", 0.2, 0.9),
        
        # 5. Frequency & Mix
        "bass_cutoff": trial.suggest_int("bass_cutoff", 150, 450),
        "piano_reverb": trial.suggest_float("piano_reverb", 0.1, 0.7),
        
        # 6. Loudness
        "target_lufs": trial.suggest_float("target_lufs", -15.0, -11.0)
    }
    return genome

def calculate_composite_score(genome: dict, analysis_results: dict):
    """
    Scores the beat by combining groove cohesion, arrangement flow, scene variety, and mix cohesion.
    """
    w_groove = 0.35
    w_flow = 0.35
    w_variety = 0.15
    w_mix = 0.15
    
    score = (
        w_groove * analysis_results.get("groove_cohesion", 1.0) +
        w_flow * analysis_results.get("flow_score", 1.0) +
        w_variety * analysis_results.get("variety_score", 1.0) +
        w_mix * analysis_results.get("mix_cohesion", 1.0)
    )
    return max(0.0, min(1.0, score))

def analyze_beat(genome: dict, blueprint: dict) -> dict:
    """
    Performs real rule-based analysis of the proposed genome and blueprint structure.
    """
    bpm = genome.get("bpm", 120)
    swing = genome.get("swing", 0.56)
    shaker_style = genome.get("shaker_style", "classic_shuffle")
    perc_syncopation = genome.get("perc_syncopation_level", 0.5)
    
    # 1. Groove Cohesion (BPM vs Swing & Shaker Style)
    groove_cohesion = 1.0
    if bpm < 118:
        # Amapiano: favors heavier swing (~0.60) and syncopated/bounce shakers
        ideal_swing = 0.60
        dist = abs(swing - ideal_swing)
        groove_cohesion -= min(0.6, dist * 6.0)
        
        if shaker_style == "straight_groove":
            groove_cohesion -= 0.3 # Penalize straight groove in Amapiano
        elif shaker_style == "classic_shuffle":
            groove_cohesion += 0.1 # Reward classic shuffle
            
        # Ideal Amapiano percussion complexity is higher (0.5 to 0.85)
        if not (0.5 <= perc_syncopation <= 0.85):
            groove_cohesion -= 0.1
    else:
        # Afro-house: favors straighter groove (~0.53) and driving shakers
        ideal_swing = 0.53
        dist = abs(swing - ideal_swing)
        groove_cohesion -= min(0.6, dist * 8.0)
        
        if shaker_style == "triplet_bounce":
            groove_cohesion -= 0.3 # Penalize triplet bounce in Afro-house
        elif shaker_style == "straight_groove":
            groove_cohesion += 0.1 # Reward straight groove
            
        # Ideal Afro-house percussion complexity is moderate (0.3 to 0.65)
        if not (0.3 <= perc_syncopation <= 0.65):
            groove_cohesion -= 0.1
        
    # 2. Arrangement Flow (Energy curve evaluation)
    scenes = blueprint.get("scenes", [])
    seq = genome.get("scene_sequence", [])
    
    flow_score = 0.8
    variety_score = 1.0
    
    if scenes and seq:
        energies = []
        for idx in seq:
            if idx < len(scenes):
                energies.append(scenes[idx].get("energy_percent", 50))
            else:
                energies.append(50)
                
        # Variety: how many unique scenes are utilized
        unique_scenes_used = len(set(seq))
        variety_score = min(1.0, unique_scenes_used / max(1, len(scenes)))
        
        # Penalize starting with immediate peak energy (> 70%)
        if energies[0] > 70:
            flow_score -= 0.15
            
        # Reward having a high energy climax/peak scene (> 80%)
        has_climax = any(e > 80 for e in energies)
        if not has_climax:
            flow_score -= 0.20
            
        # Penalize excessive consecutive repeats of the same scene
        consecutive_repeats = 0
        for i in range(len(seq) - 1):
            if seq[i] == seq[i+1]:
                consecutive_repeats += 1
        if consecutive_repeats > 2:
            flow_score -= min(0.3, consecutive_repeats * 0.05)
            
        # Evaluate standard deviation of energy levels
        energy_std = float(np.std(energies))
        if energy_std < 10.0:
            flow_score -= 0.15 # Too flat/uninteresting
        elif energy_std > 40.0:
            flow_score -= 0.1 # Too chaotic/random
            
    # 3. Frequency & Mix Cohesion
    mix_cohesion = 1.0
    bass_cutoff = genome.get("bass_cutoff", 200)
    piano_reverb = genome.get("piano_reverb", 0.3)
    if bass_cutoff > 300 and piano_reverb > 0.5:
        mix_cohesion -= 0.15
        
    return {
        "groove_cohesion": max(0.0, groove_cohesion),
        "flow_score": max(0.0, flow_score),
        "variety_score": variety_score,
        "mix_cohesion": mix_cohesion
    }

def mock_analyze_beat(genome):
    """Backward compatibility fallback."""
    return {
        "groove_cohesion": 0.8,
        "flow_score": 0.8,
        "variety_score": 0.8,
        "mix_cohesion": 0.8
    }


