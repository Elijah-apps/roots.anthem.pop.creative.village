import optuna
import random

def suggest_genome(trial: optuna.Trial, num_scenes: int = 0):
    """
    Defines the search space for a Beat Genome, now including 
    Combinatoronics (structural rearrangement).
    """
    genome = {
        # 1. Tempo & Swing
        "bpm": trial.suggest_int("bpm", 108, 126),
        "swing": trial.suggest_float("swing", 0.50, 0.70),
        
        # 2. Arrangement Structure (Combinatoronics)
        # We suggest a sequence of indices pointing to the original scenes
        "scene_sequence": [
            trial.suggest_int(f"scene_idx_{i}", 0, max(0, num_scenes - 1))
            for i in range(max(num_scenes, 8)) # Allow growing the arrangement
        ] if num_scenes > 0 else [],
        
        # 3. Density & Evolution
        "kick_density": trial.suggest_float("kick_density", 0.5, 1.0),
        "perc_density": trial.suggest_float("perc_density", 0.3, 0.9),
        
        # 4. Frequency & Mix
        "bass_cutoff": trial.suggest_int("bass_cutoff", 150, 450),
        "piano_reverb": trial.suggest_float("piano_reverb", 0.1, 0.7),
        
        # 5. Loudness
        "target_lufs": trial.suggest_float("target_lufs", -15.0, -11.0)
    }
    return genome

def calculate_composite_score(genome: dict, analysis_results: dict):
    """
    Scores the beat. Structural variety and 'flow' are prioritized.
    """
    # Structural score: penalize too many repeats of the same scene in a row
    seq = genome.get("scene_sequence", [])
    variety = len(set(seq)) / len(seq) if seq else 1.0
    
    flow_penalty = 0
    for i in range(len(seq) - 1):
        if seq[i] == seq[i+1]:
            flow_penalty += 0.05 # Deduct for stagnation
            
    groove = (genome["swing"] - 0.5) * 2.0
    
    score = (
        0.2 * variety +
        0.3 * groove +
        0.5 * analysis_results.get("harmonic_clarity", 0.8)
        - flow_penalty
    )
    return max(0, min(1.0, score))

def mock_analyze_beat(genome):
    """Simulates the analysis of the generated arrangement."""
    return {
        "harmonic_clarity": random.uniform(0.75, 0.98),
        "energy_flow": random.uniform(0.6, 0.9)
    }
