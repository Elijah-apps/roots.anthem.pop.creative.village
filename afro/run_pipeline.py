"""
run_pipeline.py
───────────────
HEX-DRIVEN & ASSET-AWARE RUNNER (Master KG Edition)
"""

import argparse
import json
import sys
import time
import hashlib
import random
import os
from pathlib import Path

# ── Specialized Brain ──
from master_kg import MasterKG

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

def optimize_beat(blueprint, n_trials=10, kg=None):
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
    
    structured_genome = {
        "bpm": best_genome.pop("bpm"),
        "swing": best_genome.pop("swing"),
        "kick_density": best_genome.pop("kick_density"),
        "perc_density": best_genome.pop("perc_density"),
        "bass_cutoff": best_genome.pop("bass_cutoff"),
        "piano_reverb": best_genome.pop("piano_reverb"),
        "target_lufs": best_genome.pop("target_lufs"),
    }
    scene_seq = []
    for i in range(max(num_scenes, 8)):
        key = f"scene_idx_{i}"
        if key in best_genome: scene_seq.append(best_genome.pop(key))
    structured_genome["scene_sequence"] = scene_seq

    print(f"\n[OPT] Best Score: {study.best_value:.4f}")
    if kg and kg.enabled:
        kg.write("opt_score", study.best_value, source="Optuna")
        kg.write("opt_lufs", structured_genome.get("target_lufs"), source="Optuna")

    return structured_genome, study.best_value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="Deep Master KG Journey")
    parser.add_argument("--blueprint", default="blueprint.json")
    parser.add_argument("--source-beat", default=None, help="Hex ID of an existing beat")
    parser.add_argument("--outdir", default="output")
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--kg", action="store_true", help="Enable Master KG Intelligence")
    parser.add_argument("--reaction", default=None)
    parser.add_argument("--lufs", type=float, default=-14.0)
    parser.add_argument("--samplerate", type=int, default=44100)
    parser.add_argument("--sf2", default=None)
    args = parser.parse_args()

    t0 = time.time()
    out_base = Path(args.outdir)

    # ── INITIALIZE MASTER KG ──
    kg = MasterKG(enabled=args.kg)
    
    # ── STEP 1: COMPOSER ──────────────────────────────────────────────────────
    banner("STEP 1: ASSET-AWARE COMPOSER")

    if args.manual:
        manual_path = Path("input/manual_blueprint.json")
        with open(manual_path, "r") as f: blueprint = json.load(f)
    elif args.source_beat:
        source_path = out_base / args.source_beat / "blueprint.json"
        with open(source_path, "r") as f: blueprint = json.load(f)
        
        # Load previous KG state if refining
        prev_kg_path = out_base / args.source_beat / "kg_state.json"
        if prev_kg_path.exists() and args.reaction:
            prev_kg = json.loads(prev_kg_path.read_text())
            kg.apply_reaction(args.reaction, prev_kg)
    else:
        step1 = load_step("01_gemini_composer")
        api_key = os.getenv("GEMINI_API_KEY")
        blueprint = step1.build_blueprint(args.prompt, api_key) if api_key else get_demo_blueprint()

    # Seed KG from blueprint (if enabled)
    kg.seed_from_blueprint(blueprint)

    # ── OPTIMIZATION ──────────────────────────────────────────────────────────
    genome = None
    opt_score = 0.5
    
    if blueprint.get("manual_optimization"):
        genome = blueprint["manual_optimization"]
        genome["bpm"] = blueprint.get("bpm", 124)
        genome["swing"] = blueprint.get("swing", 0.56)
    elif args.optimize:
        genome, opt_score = optimize_beat(blueprint, n_trials=args.trials, kg=kg)
        if "scene_sequence" in genome:
            original_scenes = blueprint.get("scenes", [])
            seen = set()
            deduped_scenes = []
            for idx in genome["scene_sequence"]:
                if idx < len(original_scenes):
                    scene = original_scenes[idx]
                    scene_key = (scene.get("name"), scene.get("energy_percent"), scene.get("bars"))
                    if scene_key not in seen:
                        seen.add(scene_key)
                        deduped_scenes.append(scene)
            if deduped_scenes:
                blueprint["scenes"] = deduped_scenes
        blueprint["bpm"] = genome.get("bpm", blueprint.get("bpm"))

    hex_id = get_hex_id(blueprint)
    if genome:
        ghash = hashlib.sha256(json.dumps(genome, sort_keys=True).encode()).hexdigest()[:4].upper()
        hex_id = f"{hex_id}_{ghash}"
    
    beat_dir = out_base / hex_id
    beat_dir.mkdir(parents=True, exist_ok=True)
    with open(beat_dir / "blueprint.json", "w") as f: json.dump(blueprint, f, indent=2)
    
    # ── STEP 2: MIDI ──────────────────────────────────────────────────────────
    banner("STEP 2: STORY-DRIVEN MIDI")
    step2 = load_step("02_midi_engine")
    step2.generate_midi(blueprint, beat_dir, genome=genome, kg=kg)

    # ── STEP 3: RENDER ────────────────────────────────────────────────────────
    banner("STEP 3: RENDERING")
    step3 = load_step("03_render_audio")
    sf_path = args.sf2 or "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    step3.render_all(beat_dir, sf_path, sample_rate=args.samplerate)

    # ── STEP 4: MASTER ────────────────────────────────────────────────────────
    banner("STEP 4: MASTERING")
    step4 = load_step("04_master")
    in_wav = beat_dir / "stems_mix.wav"
    samples, sr = step4.read_wav(in_wav)
    
    target_lufs = kg.resolve_lufs() if kg.enabled else args.lufs
    mastered = step4.master(samples, sr, target_lufs=target_lufs, kg=kg)
    
    out_wav = beat_dir / f"BEAT_{hex_id}.wav"
    step4.write_wav(out_wav, mastered, sr)
    step4.export_mp3(out_wav, beat_dir / f"BEAT_{hex_id}.mp3")

    # ── SAVE KG STATE ──
    if kg.enabled:
        kg.state["hex_id"] = hex_id
        kg.save(beat_dir / "kg_state.json")
        from rich.console import Console
        Console().print(kg.summary())

    # ── DATABASE ──
    try:
        db_mod = load_step("factory_db")
        db_mod.init_db()
        db_mod.save_beat(hex_id, blueprint.get("title", "Untitled"), blueprint.get("bpm", 124), 0.56, genome or {}, opt_score, kg_state=kg.state if kg.enabled else None)
    except: pass

    banner(f"PIPELINE COMPLETE - {hex_id}")
    print(f"Time: {time.time()-t0:.1f}s")
    print(f"Final Beat: {beat_dir / f'BEAT_{hex_id}.mp3'}")

def get_demo_blueprint():
    return {
        "title": "Hex Demo", "bpm": 124, "key": "A Minor", "selected_soundfont_id": "std_gm_01",
        "scenes": [{"name": "Intro", "energy_percent": 20, "arrangement": {"piano": "chords", "bass": "silent", "drums": "minimal"}}],
        "drums": {"kick_pattern": [1,0,0,0]*4, "snare_pattern": [0,0,0,0]*4, "hihat_pattern": [1]*16, "perc_pattern": [0]*16}
    }

if __name__ == "__main__":
    main()
