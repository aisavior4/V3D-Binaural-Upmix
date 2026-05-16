from __future__ import annotations

import argparse
import sys
from pathlib import Path

import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_batch import run_batch
from src.v3d_engine import V3DEngine


def process_single_file(input_wav: Path, output_wav: Path, preset: str) -> None:
    audio, sr = sf.read(input_wav)
    engine = V3DEngine(sr=sr)
    processed, _ = engine.process(audio, preset=preset)
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_wav, processed, sr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V3D V6.0b1 Depth & Body processing CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("single", help="Process a single WAV file")
    single.add_argument("--input", required=True, type=Path)
    single.add_argument("--output", required=True, type=Path)
    single.add_argument("--preset", choices=["ZOOM", "WIDE", "DEEP"], required=True)

    batch = subparsers.add_parser("batch", help="Process all WAV files in a folder")
    batch.add_argument("--input", required=True, type=Path)
    batch.add_argument("--output", required=True, type=Path)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "single":
        process_single_file(args.input, args.output, args.preset)
    elif args.command == "batch":
        report = run_batch(args.input, args.output)
        print(f"Batch complete. Report: {report}")
