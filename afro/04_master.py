"""
04_master.py
────────────
STEP 4 OF 4 — AI Mixing & Mastering

Applies a lightweight mastering chain to the mixed WAV from step 3:

    Low-cut HPF  →  EQ shelving  →  Soft compression
    →  Limiter  →  Loudness normalize  →  Export WAV + MP3

Usage:
    python 04_master.py
    python 04_master.py --input output/stems_mix.wav
    python 04_master.py --input output/full_mix.wav --lufs -14

Requires:
    pip install numpy scipy
    (optional) pip install pydub   — for MP3 export
    (optional) ffmpeg               — needed by pydub for MP3
"""

import argparse
import sys
import wave
from pathlib import Path

try:
    import numpy as np
    from scipy.signal import butter, sosfilt, sosfiltfilt
except ImportError:
    sys.exit("[ERROR] numpy/scipy not installed.\nRun: pip install numpy scipy")

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

# ── WAV I/O ───────────────────────────────────────────────────────────────────

def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as wf:
        n_ch = wf.getnchannels()
        sr   = wf.getframerate()
        sw   = wf.getsampwidth()
        raw  = wf.readframes(wf.getnframes())
    dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
    dtype = dtype_map.get(sw, np.int16)
    s = np.frombuffer(raw, dtype=dtype).astype(np.float64)
    s /= float(np.iinfo(dtype).max)
    if n_ch > 1:
        s = s.reshape(-1, n_ch)
    else:
        s = np.stack([s, s], axis=1)  # mono → stereo
    return s, sr


def write_wav(path: Path, samples: np.ndarray, sr: int) -> None:
    clipped = np.clip(samples, -1.0, 1.0)
    data    = (clipped * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data.tobytes())


# ── DSP building blocks ───────────────────────────────────────────────────────

def highpass(audio: np.ndarray, sr: int, cutoff_hz: float = 30.0,
             order: int = 4) -> np.ndarray:
    """Remove sub-sonic rumble below cutoff_hz."""
    sos = butter(order, cutoff_hz / (sr / 2), btype="high", output="sos")
    return sosfiltfilt(sos, audio, axis=0)


def low_shelf(audio: np.ndarray, sr: int,
              freq: float = 200.0, gain_db: float = 1.5) -> np.ndarray:
    """Boost/cut low shelf below freq Hz."""
    A  = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / 2 * np.sqrt((A + 1/A) * (1/0.707 - 1) + 2)

    b0 =     A * ((A+1) - (A-1)*np.cos(w0) + 2*np.sqrt(A)*alpha)
    b1 = 2 * A * ((A-1) - (A+1)*np.cos(w0))
    b2 =     A * ((A+1) - (A-1)*np.cos(w0) - 2*np.sqrt(A)*alpha)
    a0 =           (A+1) + (A-1)*np.cos(w0) + 2*np.sqrt(A)*alpha
    a1 =    -2 *  ((A-1) + (A+1)*np.cos(w0))
    a2 =           (A+1) + (A-1)*np.cos(w0) - 2*np.sqrt(A)*alpha

    sos = np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])
    return sosfiltfilt(sos, audio, axis=0)


def high_shelf(audio: np.ndarray, sr: int,
               freq: float = 10000.0, gain_db: float = 1.0) -> np.ndarray:
    """Add air / presence above freq Hz."""
    A  = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sr
    alpha = np.sin(w0) / 2 * np.sqrt((A + 1/A) * (1/0.707 - 1) + 2)

    b0 =     A * ((A+1) + (A-1)*np.cos(w0) + 2*np.sqrt(A)*alpha)
    b1 =-2 * A * ((A-1) + (A+1)*np.cos(w0))
    b2 =     A * ((A+1) + (A-1)*np.cos(w0) - 2*np.sqrt(A)*alpha)
    a0 =           (A+1) - (A-1)*np.cos(w0) + 2*np.sqrt(A)*alpha
    a1 = 2  *     ((A-1) - (A+1)*np.cos(w0))
    a2 =           (A+1) - (A-1)*np.cos(w0) - 2*np.sqrt(A)*alpha

    sos = np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])
    return sosfiltfilt(sos, audio, axis=0)


def soft_compressor(audio: np.ndarray,
                    threshold_db: float = -18.0,
                    ratio: float = 3.0,
                    attack_ms: float = 10.0,
                    release_ms: float = 100.0,
                    sr: int = 44100) -> np.ndarray:
    """
    Simple RMS-based soft-knee compressor.
    Optimized with vectorized level tracking and gain application.
    """
    threshold = 10 ** (threshold_db / 20.0)
    attack    = np.exp(-1.0 / (sr * attack_ms  / 1000.0))
    release   = np.exp(-1.0 / (sr * release_ms / 1000.0))

    # Pre-calculate absolute max level per sample across all channels
    levels = np.max(np.abs(audio), axis=1)

    # Fast scalar loop in Python to compute the envelope
    envs = np.zeros(len(audio))
    curr_env = 0.0
    for i in range(len(audio)):
        level = levels[i]
        if level > curr_env:
            curr_env = attack * curr_env + (1.0 - attack) * level
        else:
            curr_env = release * curr_env + (1.0 - release) * level
        envs[i] = curr_env

    # Vectorized gain application
    gains = np.ones(len(audio))
    mask = envs > threshold
    if np.any(mask):
        gains[mask] = (threshold + (envs[mask] - threshold) / ratio) / envs[mask]

    # Apply gains
    output = audio * gains[:, np.newaxis]
    return output



def limiter(audio: np.ndarray, ceiling_db: float = -0.3) -> np.ndarray:
    """Hard brick-wall limiter."""
    ceiling = 10 ** (ceiling_db / 20.0)
    peak    = np.max(np.abs(audio))
    if peak > ceiling:
        audio = audio * (ceiling / peak)
    return audio


def loudness_normalize(audio: np.ndarray, target_lufs: float = -14.0,
                        sr: int = 44100) -> np.ndarray:
    """
    Simplified integrated loudness normalisation (approximates ITU-R BS.1770).
    Uses RMS as a proxy for integrated loudness.
    """
    rms_actual = np.sqrt(np.mean(audio ** 2))
    if rms_actual < 1e-9:
        return audio
    target_rms = 10 ** (target_lufs / 20.0) * 0.7  # rough LUFS→RMS mapping
    gain = target_rms / rms_actual
    gain = min(gain, 6.0)  # cap at +6 dB to avoid over-amplification
    return audio * gain


# ── Mastering chain ───────────────────────────────────────────────────────────

def master(samples: np.ndarray, sr: int,
           target_lufs: float = -14.0, kg=None) -> np.ndarray:
    """
    Full mastering chain:
        HPF → Low shelf → High shelf → Compressor → Limiter → LUFS normalize

    When a MasterKG is provided and enabled, all DSP parameters are resolved
    from genre + emotion intelligence (Amapiano vs Afro-house presets,
    Optuna-optimised LUFS, reaction-driven EQ deltas).
    """
    # Resolve DSP parameters from KG or use safe defaults
    if kg and kg.enabled:
        dsp = kg.resolve_master_dsp()
        target_lufs       = dsp.get("target_lufs",      target_lufs)
        low_shelf_freq    = dsp.get("low_shelf_freq",   200.0)
        low_shelf_gain    = dsp.get("low_shelf_gain",   1.5)
        high_shelf_freq   = dsp.get("high_shelf_freq",  10000.0)
        high_shelf_gain   = dsp.get("high_shelf_gain",  1.0)
        comp_threshold_db = dsp.get("comp_threshold_db", -18.0)
        comp_ratio        = dsp.get("comp_ratio",        3.0)
        comp_attack_ms    = dsp.get("comp_attack_ms",    10.0)
        comp_release_ms   = dsp.get("comp_release_ms",   100.0)
        genre = kg.read("genre", "afro-house")
        print(f"  [Master/KG] Genre: {genre} | LUFS: {target_lufs} | "
              f"Low shelf: +{low_shelf_gain}dB | Comp ratio: {comp_ratio}:1")
    else:
        low_shelf_freq    = 200.0
        low_shelf_gain    = 1.5
        high_shelf_freq   = 10000.0
        high_shelf_gain   = 1.0
        comp_threshold_db = -18.0
        comp_ratio        = 3.0
        comp_attack_ms    = 10.0
        comp_release_ms   = 100.0

    print("  [Master] High-pass filter  (30 Hz)...")
    s = highpass(samples, sr, cutoff_hz=30.0)

    print(f"  [Master] Low shelf boost   (+{low_shelf_gain} dB @ {int(low_shelf_freq)} Hz)...")
    s = low_shelf(s, sr, freq=low_shelf_freq, gain_db=low_shelf_gain)

    print(f"  [Master] High shelf boost  (+{high_shelf_gain} dB @ {int(high_shelf_freq)} Hz)...")
    s = high_shelf(s, sr, freq=high_shelf_freq, gain_db=high_shelf_gain)

    print(f"  [Master] Compressor        ({comp_threshold_db} dB threshold, {comp_ratio}:1 ratio)...")
    s = soft_compressor(s, threshold_db=comp_threshold_db, ratio=comp_ratio,
                        attack_ms=comp_attack_ms, release_ms=comp_release_ms, sr=sr)

    print(f"  [Master] Loudness normalize ({target_lufs} LUFS)...")
    s = loudness_normalize(s, target_lufs=target_lufs, sr=sr)

    print("  [Master] Brick-wall limiter (-0.3 dBFS)...")
    s = limiter(s, ceiling_db=-0.3)

    return s


# ── MP3 export ────────────────────────────────────────────────────────────────

def export_mp3(wav_path: Path, mp3_path: Path, bitrate: str = "320k") -> bool:
    if not HAS_PYDUB:
        print("[INFO] pydub not installed — skipping MP3 export. "
              "Install with: pip install pydub  (+ ffmpeg)")
        return False
    try:
        seg = AudioSegment.from_wav(str(wav_path))
        seg.export(str(mp3_path), format="mp3", bitrate=bitrate)
        size_kb = mp3_path.stat().st_size // 1024
        print(f"[MP3] Exported → {mp3_path}  ({size_kb} KB)")
        return True
    except Exception as exc:
        print(f"[WARN] MP3 export failed: {exc}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Step 4 — Master the mixed WAV and export final beat")
    parser.add_argument("--input", default=None,
                        help="Input WAV file (default: output/stems_mix.wav, "
                             "fallback: output/full_mix.wav)")
    parser.add_argument("--outdir", default="output",
                        help="Output directory")
    parser.add_argument("--lufs", type=float, default=-14.0,
                        help="Target integrated loudness (default -14 LUFS)")
    parser.add_argument("--mp3-bitrate", default="320k",
                        help="MP3 export bitrate (default 320k)")
    args = parser.parse_args()

    outdir = Path(args.outdir)

    # resolve input file
    if args.input:
        in_path = Path(args.input)
    else:
        candidates = [
            outdir / "stems_mix.wav",
            outdir / "full_mix.wav",
        ]
        in_path = next((p for p in candidates if p.exists()), None)
        if in_path is None:
            sys.exit(
                f"[ERROR] No input WAV found in {outdir}/\n"
                "Run 03_render_audio.py first."
            )

    print(f"\n[Master] Input  → {in_path}")

    samples, sr = read_wav(in_path)
    print(f"[Master] Loaded  {len(samples)/sr:.1f}s  |  {sr} Hz  |  stereo")

    mastered = master(samples, sr, target_lufs=args.lufs)

    # save mastered WAV
    out_wav = outdir / "MASTER.wav"
    write_wav(out_wav, mastered, sr)
    size_mb = out_wav.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Master WAV → {out_wav}  ({size_mb:.1f} MB)")

    # optional MP3
    out_mp3 = outdir / "MASTER.mp3"
    export_mp3(out_wav, out_mp3, bitrate=args.mp3_bitrate)

    print("\n[DONE] Mastering complete.")
    print(f"  Final beat: {out_wav}")
    if out_mp3.exists():
        print(f"  MP3 copy:   {out_mp3}")


if __name__ == "__main__":
    main()