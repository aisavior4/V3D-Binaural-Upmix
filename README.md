# V3D-Binaural-Upmix

V3D is a mobile video spatial audio engine that transforms smartphone video audio into headphone-friendly spatial/binaural output.

- **V5.x**: Stereo Enhancement
- **V6.x**: Spatial Reconstruction for mobile video

V6.0b1 focuses on **camera-perspective front cues**, **depth**, **body preservation**, and **width support**. Elevation/SKY/AIR processing is intentionally postponed.

## Presets

- **ZOOM**: Close, focused, front-oriented presentation. Keeps center/body stable with only mild presence enhancement.
- **WIDE**: Wider ambience while preserving low-mid body and center stability.
- **DEEP**: Farther, darker, and more immersive effect using zero-padded delay, high-frequency rolloff, and mild level reduction.

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
- `*_zoom.wav`
- `*_wide.wav`
- `*_deep.wav`

The batch report includes:
- `file`
- `preset`
- `sample_rate`
- `peak_in_dbfs`
- `peak_out_dbfs`
- `rms_in`
- `rms_out`
- `phase_corr_in`
- `phase_corr_out`
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
- Dry center preservation is prioritized over analyzer-only optimization.
- Perplexity Computer integration preparation: batch report schema is fixed and ready for QA ingestion.
