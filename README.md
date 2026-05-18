# V3D-Binaural-Upmix

V3D is a mobile video spatial audio engine that transforms smartphone video audio into headphone-friendly spatial/binaural output.

- **V5.x**: Stereo Enhancement
- **V6.x**: Spatial Reconstruction for mobile video

V6.0b2 is a correction to V6.0b1 and now uses **parallel dry + wet processing**:

**Output = Dry original 100% + subtle Wet spatial layer**

This keeps the source body/center intact while adding only small spatial cues. Elevation/SKY/AIR processing remains intentionally postponed.

## Presets

- **ORIGINAL**: Unchanged copy of the input for immediate A/B comparison.
- **ZOOM**: Very close to original with only subtle presence wet support.
- **WIDE**: Dry 100% plus side-only wet widening layer.
- **DEEP**: Dry 100% plus delayed darker ambience/reflection wet layer.


## V6.2 Tuning Notes

V6.2 focuses on **energy/body recovery while preserving spatial expansion** from V6.0b2.

Key DSP updates:
- Stronger **center/mid anchor**: dry remains dominant, wet stays subtle.
- Added **low-mid recovery (120-350 Hz)** to recover body/impact.
- Added **air/presence recovery (8-12 kHz)** to reduce dull/recessed tone.
- Added light **transient support** to retain attack and clarity.
- **DEEP** mode low-pass is relaxed (less dark), with anti-collapse side support.
- Near-mono detection in DEEP keeps stereo decorrelation subtle and phase-safe.

Expected listening effect by preset:
- **ZOOM**: closer to original impact, less weak/recessed.
- **WIDE**: still wide, but with better body and less hollow center feeling.
- **DEEP**: deeper ambience without collapsing toward mono, with improved clarity.

Safety posture:
- Dry path remains primary.
- No source separation.
- Peak safety scaling retained.

## Installation

```bash
pip install -r requirements.txt
```

## WAV Batch Usage

Run all WAV files in an input folder and generate all preset outputs plus `report.csv`:

```bash
python scripts/run_batch.py --input ./input --output ./output
```

Each input file produces:
- `*_original.wav`
- `*_zoom.wav`
- `*_wide.wav`
- `*_deep.wav`

The batch report includes:
- `file`
- `preset`
- `sample_rate`
- `peak_in_dbfs`
- `peak_out_dbfs`
- `peak_delta_db`
- `rms_in`
- `rms_out`
- `rms_delta_db`
- `phase_corr_in`
- `phase_corr_out`
- `phase_corr_delta`
- `side_ratio_in`
- `side_ratio_out`
- `safety_gain_db`
- `output_path`

## CLI Wrapper Usage

Single file:

```bash
python src/main.py single --input ./input/test.wav --output ./output/test_deep.wav --preset DEEP
```

Batch:

```bash
python src/main.py batch --input ./input --output ./output
```

## Notes

- No source separation is used in this phase.
- Dry center/body preservation is prioritized over analyzer-only optimization.
- Perplexity Computer integration remains QA/research preparation only.
