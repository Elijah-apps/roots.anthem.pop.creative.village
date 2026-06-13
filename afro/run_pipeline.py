"""
run_pipeline.py
───────────────
HEX-DRIVEN & ASSET-AWARE RUNNER
"""

import argparse
import json
import sys
import time
import hashlib
import random
import os
from pathlib import Path

# ── Step Loader ───────────────────────────────────────────────────────────────
def load_step(stem: str):
    import importlib.util
    path = Path(__file__).parent / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(stem, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def banner(title: str):
    print(f"\n{'═' * 60}\n  {title}\n{'═' * 60}")

def get_hex_id(data: dict) -> str:
    """Generate an 8-char hex ID from the blueprint content."""
    s = json.dumps(data, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:8].upper()

def optimize_beat(blueprint, n_trials=10):
    banner("COMBINATORONICS OPTIMIZATION MODE (OPTUNA)")
    import optuna
    opt_mod = load_step("optimization_engine")
    
    num_scenes = len(blueprint.get("scenes", []))
    
    def objective(trial):
        genome = opt_mod.suggest_genome(trial, num_scenes=num_scenes)
        analysis = opt_mod.mock_analyze_beat(genome)
        score = opt_mod.calculate_composite_score(genome, analysis)
        return score

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    
    best_genome = study.best_params
    
    # Reconstruct the genome dict (Optuna flattens it)
    structured_genome = {
        "bpm": best_genome.pop("bpm"),
        "swing": best_genome.pop("swing"),
        "kick_density": best_genome.pop("kick_density"),
        "perc_density": best_genome.pop("perc_density"),
        "bass_cutoff": best_genome.pop("bass_cutoff"),
        "piano_reverb": best_genome.pop("piano_reverb"),
        "target_lufs": best_genome.pop("target_lufs"),
    }
    # Gather scene sequence
    scene_seq = []
    for i in range(max(num_scenes, 8)):
        key = f"scene_idx_{i}"
        if key in best_genome:
            scene_seq.append(best_genome.pop(key))
    structured_genome["scene_sequence"] = scene_seq

    print(f"\n[OPT] Best Score: {study.best_value:.4f}")
    print(f"[OPT] Best Genome: {json.dumps(structured_genome, indent=2)}")
    return structured_genome, study.best_value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Deep Master KG Journey")
    parser.add_argument("--blueprint", default="blueprint.json")
    parser.add_argument("--source-beat", default=None, help="Hex ID of an existing beat to rearrange")
    parser.add_argument("--outdir", default="output")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--skip-gemini", action="store_true", help="Use existing blueprint")
    parser.add_argument("--skip-render", action="store_true", help="Stop after MIDI generation")
    parser.add_argument("--sf2", default=None, help="Path to .sf2 SoundFont")
    parser.add_argument("--lufs", type=float, default=-14.0, help="Target loudness")
    parser.add_argument("--samplerate", type=int, default=44100, help="Sample rate")
    parser.add_argument("--optimize", action="store_true", help="Run genetic optimization")
    parser.add_argument("--trials", type=int, default=10, help="Number of optimization trials")
    parser.add_argument("--manual", action="store_true", help="Load from input/manual_blueprint.json")
    args = parser.parse_args()

    t0 = time.time()
    out_base = Path(args.outdir)
    out_base.mkdir(parents=True, exist_ok=True)

    # ── STEP 1: COMPOSER ──────────────────────────────────────────────────────
    banner("STEP 1: ASSET-AWARE COMPOSER")

    if args.manual:
        manual_path = Path("input/manual_blueprint.json")
        if not manual_path.exists():
            sys.exit(f"[ERROR] Manual blueprint not found at {manual_path}. Please paste your AI result there.")
        print(f"[INFO] Loading MANUAL blueprint from {manual_path}")
        with open(manual_path, "r") as f:
            blueprint = json.load(f)
    elif args.source_beat:

        source_path = out_base / args.source_beat / "blueprint.json"
        if not source_path.exists():
            sys.exit(f"[ERROR] Source beat {args.source_beat} not found at {source_path}")
        print(f"[INFO] Rearranging existing beat: {args.source_beat}")
        with open(source_path, "r") as f:
            blueprint = json.load(f)
    elif args.skip_gemini:
        print(f"[INFO] Skipping Gemini, loading {args.blueprint}")
        with open(args.blueprint, "r") as f:
            blueprint = json.load(f)
    else:
        step1 = load_step("01_gemini_composer")
        api_key = args.api_key or os.getenv("GEMINI_API_KEY")
        
        if api_key:
            blueprint = step1.build_blueprint(args.prompt, api_key)
        else:
            print("[WARN] No API key, using demo blueprint.")
            blueprint = get_demo_blueprint()

    # ── OPTIMIZATION ──────────────────────────────────────────────────────────
    genome = None
    opt_score = 0.5 # default
    
    # CHECK FOR DEEP MANUAL OVERRIDE
    if blueprint.get("manual_optimization"):
        banner("DEEP MANUAL OVERRIDE DETECTED")
        genome = blueprint["manual_optimization"]
        # Ensure base genome fields are present
        genome["bpm"] = blueprint.get("bpm", 124)
        genome["swing"] = blueprint.get("swing", 0.56)
        print("[INFO] Using manual production parameters from blueprint.")
        opt_score = 1.0 # Perfect match of user intent
    elif args.optimize:
        genome, opt_score = optimize_beat(blueprint, n_trials=args.trials)
        
        # APPLY COMBINATORONICS (Rearrangement)
        if "scene_sequence" in genome:
            original_scenes = blueprint.get("scenes", [])
            new_scenes = []
            for idx in genome["scene_sequence"]:
                if idx < len(original_scenes):
                    new_scenes.append(original_scenes[idx])
            blueprint["scenes"] = new_scenes
            print(f"[COMB] Rearranged {len(original_scenes)} scenes into sequence of {len(new_scenes)}")
        
        blueprint["bpm"] = genome.get("bpm", blueprint.get("bpm"))

    # GENERATE HEX ID
    hex_id = get_hex_id(blueprint)
    if genome:
        ghash = hashlib.sha256(json.dumps(genome, sort_keys=True).encode()).hexdigest()[:4].upper()
        hex_id = f"{hex_id}_{ghash}"

    print(f"[HEX] Beat Identifier: {hex_id}")
    
    beat_dir = out_base / hex_id
    beat_dir.mkdir(parents=True, exist_ok=True)
    
    with open(beat_dir / "blueprint.json", "w") as f:
        json.dump(blueprint, f, indent=2)
    if genome:
        with open(beat_dir / "genome.json", "w") as f:
            json.dump(genome, f, indent=2)

    # ── STEP 2: MIDI ──────────────────────────────────────────────────────────
    banner("STEP 2: STORY-DRIVEN MIDI")
    step2 = load_step("02_midi_engine")
    step2.generate_midi(blueprint, beat_dir, genome=genome)

    if args.skip_render:
        banner(f"MIDI GENERATION COMPLETE - {hex_id}")
        return

    # ── STEP 3: RENDER ────────────────────────────────────────────────────────
    banner("STEP 3: RENDERING WITH ASSET AWARENESS")
    step3 = load_step("03_render_audio")
    
    # Resolve SoundFont
    sf_path = args.sf2
    if not sf_path:
        sf_id = blueprint.get("selected_soundfont_id")
        registry = blueprint.get("_registry", {"soundfonts": []})
        sf_path = "/usr/share/sounds/sf2/FluidR3_GM.sf2" # Fallback
        
        for sf in registry.get("soundfonts", []):
            if sf["id"] == sf_id:
                sf_path = sf["path"]
                print(f"[ASSET] Using SoundFont from Registry: {sf['name']} ({sf_id})")
                break

    step3.render_all(beat_dir, sf_path, sample_rate=args.samplerate)

    # ── STEP 4: MASTER ────────────────────────────────────────────────────────
    banner("STEP 4: MASTERING")
    step4 = load_step("04_master")
    
    in_wav = beat_dir / "stems_mix.wav"
    samples, sr = step4.read_wav(in_wav)
    target_lufs = genome.get("target_lufs", args.lufs) if genome else args.lufs
    
    mastered = step4.master(samples, sr, target_lufs=target_lufs)
    
    out_wav = beat_dir / f"BEAT_{hex_id}.wav"
    step4.write_wav(out_wav, mastered, sr)
    
    out_mp3 = beat_dir / f"BEAT_{hex_id}.mp3"
    step4.export_mp3(out_wav, out_mp3)

    # ── DATABASE ──────────────────────────────────────────────────────────────
    try:
        db_mod = load_step("factory_db")
        db_mod.init_db()
        db_mod.save_beat(
            hex_id=hex_id,
            title=blueprint.get("title", "Untitled"),
            bpm=blueprint.get("bpm", 124),
            swing=genome.get("swing", 0.56) if genome else 0.56,
            genome=genome or {},
            score=opt_score
        )
        print(f"[DB] Beat saved to factory database.")
    except Exception as e:
        print(f"[DB] Error saving to database: {e}")

    banner(f"PIPELINE COMPLETE - {hex_id}")
    print(f"Time: {time.time()-t0:.1f}s")
    print(f"Final Beat: {out_mp3}")

def get_demo_blueprint():
    return {
        "title": "Hex Demo",
        "bpm": 124,
        "key": "A Minor",
        "selected_soundfont_id": "std_gm_01",
        "global_motifs": {
            "piano_main": [["A4", 1.0], ["E5", 1.0]],
            "bass_main": [["A1", 2.0]],
            "vocal_hook": [["A5", 4.0]]
        },
        "scenes": [
            {
                "name": "Intro",
                "emotion": "Curiosity",
                "energy_percent": 20,
                "bars": 4,
                "arrangement": {"piano": "chords", "bass": "silent", "drums": "silent"}
            },
            {
                "name": "Peak",
                "emotion": "Euphoria",
                "energy_percent": 90,
                "bars": 8,
                "arrangement": {"piano": "motif", "bass": "driving", "drums": "full"}
            }
        ],
        "drums": {"kick_pattern": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0], "snare_pattern": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0], "hihat_pattern": [1]*16, "perc_pattern": [0]*16},
        "_registry": {
            "soundfonts": [{"id": "std_gm_01", "name": "FluidR3", "path": "/usr/share/sounds/sf2/FluidR3_GM.sf2"}]
        }
    }

if __name__ == "__main__":
    main()
