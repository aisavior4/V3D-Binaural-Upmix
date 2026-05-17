from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.v3d_engine import V3DEngine

PRESETS = ("ORIGINAL", "ZOOM", "WIDE", "DEEP")


def dbfs_peak(x: np.ndarray) -> float:
    peak = float(np.max(np.abs(x))) if x.size else 0.0
    return -120.0 if peak <= 0 else 20.0 * np.log10(peak)


def rms(x: np.ndarray) -> float:
    if not x.size:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x))))


def phase_corr(stereo: np.ndarray) -> float:
    l = stereo[:, 0]
    r = stereo[:, 1]
    denom = np.sqrt(np.sum(l * l) * np.sum(r * r))
    if denom <= 0:
        return 0.0
    return float(np.sum(l * r) / denom)


def side_ratio(stereo: np.ndarray) -> float:
    mid = 0.5 * (stereo[:, 0] + stereo[:, 1])
    side = 0.5 * (stereo[:, 0] - stereo[:, 1])
    mid_rms = rms(mid)
    side_rms = rms(side)
    if mid_rms <= 1e-12:
        return 0.0
    return float(side_rms / mid_rms)


def run_batch(input_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    wav_files = sorted(input_dir.glob("*.wav"))
    report_path = output_dir / "report.csv"

    rows = []
    for wav_path in wav_files:
        audio, sr = sf.read(wav_path)
        engine = V3DEngine(sr=sr)
        x = engine.ensure_stereo(np.asarray(audio, dtype=np.float32))

        peak_in = dbfs_peak(x)
        rms_in = rms(x)
        phase_in = phase_corr(x)
        side_in = side_ratio(x)

        for preset in PRESETS:
            y, meta = engine.process(x, preset=preset)
            out_name = f"{wav_path.stem}_{preset.lower()}.wav"
            out_path = output_dir / out_name
            sf.write(out_path, y, sr)

            peak_out = dbfs_peak(y)
            rms_out = rms(y)
            phase_out = phase_corr(y)
            side_out = side_ratio(y)

            rows.append(
                {
                    "file": wav_path.name,
                    "preset": preset,
                    "sample_rate": sr,
                    "peak_in_dbfs": f"{peak_in:.4f}",
                    "peak_out_dbfs": f"{peak_out:.4f}",
                    "rms_in": f"{rms_in:.6f}",
                    "rms_out": f"{rms_out:.6f}",
                    "rms_delta_db": f"{20.0 * np.log10(max(rms_out, 1e-12) / max(rms_in, 1e-12)):.4f}",
                    "phase_corr_in": f"{phase_in:.6f}",
                    "phase_corr_out": f"{phase_out:.6f}",
                    "phase_corr_delta": f"{(phase_out - phase_in):.6f}",
                    "side_ratio_in": f"{side_in:.6f}",
                    "side_ratio_out": f"{side_out:.6f}",
                    "peak_delta_db": f"{(peak_out - peak_in):.4f}",
                    "safety_gain_db": f"{meta['safety_gain_db']:.4f}",
                    "output_path": str(out_path),
                }
            )

    rows.sort(key=lambda row: (row["file"], PRESETS.index(row["preset"])))

    with report_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "file",
                "preset",
                "sample_rate",
                "peak_in_dbfs",
                "peak_out_dbfs",
                "peak_delta_db",
                "rms_in",
                "rms_out",
                "rms_delta_db",
                "phase_corr_in",
                "phase_corr_out",
                "phase_corr_delta",
                "side_ratio_in",
                "side_ratio_out",
                "safety_gain_db",
                "output_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run V3D V6.0b2 WAV batch processing.")
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input folder containing WAV files",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output folder",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    path = run_batch(args.input, args.output)
    print(f"Wrote report: {path}")
