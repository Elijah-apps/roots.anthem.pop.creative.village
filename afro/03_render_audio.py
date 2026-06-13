"""
03_render_audio.py
──────────────────
STEP 3 OF 4 — Instrument Rendering

Renders each MIDI file from step 2 to WAV using FluidSynth and a
General MIDI soundfont (.sf2). Each instrument track gets its own
WAV, then all tracks are mixed together into a single stereo WAV.

Usage:
    python 03_render_audio.py
    python 03_render_audio.py --sf2 soundfonts/FluidR3_GM.sf2
    python 03_render_audio.py --outdir output/ --samplerate 48000

Requires:
    fluidsynth  (apt install fluidsynth  /  brew install fluidsynth)
    pip install numpy scipy
    (optional) pip install soundfile  — for better WAV I/O
"""

import argparse
import subprocess
import sys
import wave
from pathlib import Path

try:
    import numpy as np
except ImportError:
    sys.exit("[ERROR] numpy not installed.\nRun: pip install numpy")

# Optional: soundfile for professional WAV read/write
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

# ── FluidSynth wrapper ────────────────────────────────────────────────────────

DEFAULT_SF2 = "soundfonts/FluidR3_GM.sf2"


def find_fluidsynth() -> str:
    """Return the fluidsynth binary path, or raise if not found."""
    import shutil
    path = shutil.which("fluidsynth")
    if path:
        return path
    raise FileNotFoundError(
        "fluidsynth not found.\n"
        "Install with:  sudo apt install fluidsynth   OR   brew install fluidsynth"
    )


def render_midi_to_wav(midi_path: Path, wav_path: Path,
                        sf2_path: str, sample_rate: int = 44100) -> bool:
    """
    Call FluidSynth to render a MIDI file to WAV.
    Returns True on success.
    """
    fluids = find_fluidsynth()

    cmd = [
        fluids,
        "-ni",                       # non-interactive
        "-g", "1.5",                 # gain
        "-r", str(sample_rate),      # sample rate
        sf2_path,
        str(midi_path),
        "-F", str(wav_path),         # output file
    ]

    print(f"  [FluidSynth] {midi_path.name} → {wav_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [ERROR] FluidSynth failed on {midi_path.name}:")
        print(result.stderr[-300:])
        return False

    if wav_path.exists() and wav_path.stat().st_size > 1000:
        dur = get_wav_duration(wav_path)
        print(f"  [OK] {wav_path.name}  ({dur:.1f}s)")
        return True
    else:
        print(f"  [ERROR] Output WAV missing or too small: {wav_path}")
        return False


# ── WAV mixing helpers ────────────────────────────────────────────────────────

def read_wav(path: Path) -> tuple[np.ndarray, int]:
    """Read a WAV file. Returns (samples float32 array, sample_rate)."""
    with wave.open(str(path), "rb") as wf:
        n_channels  = wf.getnchannels()
        sample_rate = wf.getframerate()
        sampwidth   = wf.getsampwidth()
        n_frames    = wf.getnframes()
        raw         = wf.readframes(n_frames)

    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sampwidth, np.int16)
    samples = np.frombuffer(raw, dtype=dtype).astype(np.float32)

    # normalise to [-1, 1]
    samples /= float(np.iinfo(dtype).max)

    # reshape to (frames, channels)
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels)
    else:
        samples = samples.reshape(-1, 1)

    # make stereo
    if samples.shape[1] == 1:
        samples = np.hstack([samples, samples])

    return samples, sample_rate


def write_wav(path: Path, samples: np.ndarray, sample_rate: int) -> None:
    """Write float32 stereo samples to a 16-bit WAV file."""
    clipped = np.clip(samples, -1.0, 1.0)
    data    = (clipped * 32767).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data.tobytes())


def get_wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


# ── Per-track gain map ────────────────────────────────────────────────────────
TRACK_GAINS = {
    "piano":       0.70,
    "bass":        0.85,
    "log_drum":    0.82,
    "drums":       0.75,
    "vocal_guide": 0.55,
    "full_mix":    0.90,
}



def mix_wav_files(wav_paths: list[Path], output_path: Path,
                  track_gains: dict | None = None) -> None:
    """
    Mix multiple WAV files into one stereo output with individual gains.
    Pads shorter files with silence; normalises the final mix.
    """
    if not wav_paths:
        print("[WARN] No WAV files to mix.")
        return

    track_gains = track_gains or {}

    # load all tracks
    tracks    = []
    max_len   = 0
    sample_rate = 44100

    for p in wav_paths:
        samples, sr = read_wav(p)
        sample_rate = sr
        name  = p.stem
        gain  = track_gains.get(name, 0.80)
        
        # Apply panning to spread the stereo field
        track_samples = samples * gain
        if name == "piano":
            # Pan slightly left
            track_samples = track_samples * np.array([1.12, 0.88])
        elif name == "vocal_guide":
            # Pan slightly right
            track_samples = track_samples * np.array([0.88, 1.12])
            
        tracks.append((track_samples, name))
        max_len = max(max_len, len(samples))


    # pad & sum
    mix = np.zeros((max_len, 2), dtype=np.float32)
    for samples, name in tracks:
        pad = np.zeros((max_len - len(samples), 2), dtype=np.float32)
        padded = np.vstack([samples, pad])
        mix += padded

    # normalise (peak normalise to -0.5 dBFS)
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.944

    write_wav(output_path, mix, sample_rate)
    print(f"[Mix] Master mix → {output_path}  ({get_wav_duration(output_path):.1f}s)")


# ── Main ──────────────────────────────────────────────────────────────────────

def render_all(outdir: Path, sf2_path: str, sample_rate: int = 44100) -> None:
    midi_files = sorted(outdir.glob("*.mid"))
    if not midi_files:
        sys.exit(f"[ERROR] No MIDI files found in {outdir}/\n"
                 "Run 02_midi_engine.py first.")

    print(f"\n[Render] Found {len(midi_files)} MIDI file(s). Using SF2: {sf2_path}\n")

    rendered = []
    for midi_path in midi_files:
        wav_path = outdir / (midi_path.stem + ".wav")
        ok = render_midi_to_wav(midi_path, wav_path, sf2_path, sample_rate)
        if ok:
            rendered.append(wav_path)

    if not rendered:
        sys.exit("[ERROR] No WAV files were rendered successfully.")

    # Mix individual stems (exclude full_mix.wav from stems mix)
    stems = [w for w in rendered if w.stem != "full_mix"]

    if stems:
        stems_mix_path = outdir / "stems_mix.wav"
        print(f"\n[Mix] Mixing {len(stems)} stems...")
        mix_wav_files(stems, stems_mix_path, track_gains=TRACK_GAINS)

    print(f"\n[DONE] Rendered {len(rendered)} WAV file(s) to {outdir}/")


def main():
    parser = argparse.ArgumentParser(
        description="Step 3 — Render MIDI to WAV via FluidSynth")
    parser.add_argument("--outdir", default="output",
                        help="Directory containing MIDI files (also for WAV output)")
    parser.add_argument("--sf2", default=DEFAULT_SF2,
                        help="Path to .sf2 SoundFont file")
    parser.add_argument("--samplerate", type=int, default=44100,
                        help="Audio sample rate (default 44100)")
    args = parser.parse_args()

    sf2 = args.sf2
    if not Path(sf2).exists():
        # try system sf2 locations
        fallbacks = [
            "/usr/share/sounds/sf2/FluidR3_GM.sf2",
            "/usr/share/sounds/sf2/TimGM6mb.sf2",
            "/usr/local/share/fluidsynth/GeneralUser_GS.sf2",
        ]
        for fb in fallbacks:
            if Path(fb).exists():
                sf2 = fb
                print(f"[INFO] Using system SoundFont: {sf2}")
                break
        else:
            sys.exit(
                f"[ERROR] SoundFont not found at {args.sf2}\n"
                "Download one from:  https://musescore.org/en/handbook/3/soundfonts-and-sfz-files"
            )

    render_all(Path(args.outdir), sf2, args.samplerate)


if __name__ == "__main__":
    main()