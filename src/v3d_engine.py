from __future__ import annotations

from typing import Dict

import numpy as np
from scipy import signal


class V3DEngine:
    """V6.0b2 parallel dry+wet engine for mobile-video stereo sources."""

    def __init__(self, sr: int = 48000) -> None:
        self.sr = sr

    def ensure_stereo(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return np.stack([x, x], axis=1)
        if x.shape[1] == 1:
            return np.concatenate([x, x], axis=1)
        return x[:, :2]

    def safe_peak_scale(
        self,
        x: np.ndarray,
        headroom_db: float = -1.0,
    ) -> tuple[np.ndarray, float]:
        peak = float(np.max(np.abs(x))) if x.size else 0.0
        target_peak = 10 ** (headroom_db / 20.0)

        if peak <= 0.0 or peak <= target_peak:
            return x, 0.0

        gain = target_peak / peak
        gain_db = 20.0 * np.log10(gain)
        return x * gain, gain_db

    def zero_pad_delay(self, x: np.ndarray, delay_samples: int) -> np.ndarray:
        if delay_samples <= 0:
            return x.copy()

        delayed = np.zeros_like(x)
        delayed[delay_samples:] = x[:-delay_samples]
        return delayed

    def force_pseudo_stereo(
        self,
        x: np.ndarray,
        delay_ms: float = 0.25,
        blend: float = 0.10,
    ) -> np.ndarray:
        delay_samples = max(1, int(self.sr * delay_ms / 1000.0))

        delayed_l = self.zero_pad_delay(x[:, [0]], delay_samples)[:, 0]
        delayed_r = self.zero_pad_delay(x[:, [1]], delay_samples)[:, 0]

        out_l = (1.0 - blend) * x[:, 0] + blend * delayed_r
        out_r = (1.0 - blend) * x[:, 1] + blend * delayed_l
        return np.stack([out_l, out_r], axis=1)

    def process_original(self, dry: np.ndarray) -> np.ndarray:
        return dry.copy()

    def process_zoom(self, dry: np.ndarray) -> np.ndarray:
        mid = 0.5 * (dry[:, 0] + dry[:, 1])
        b, a = signal.butter(1, 3600 / (self.sr / 2.0), btype="high")
        presence = signal.lfilter(b, a, mid)
        wet = np.stack([presence, presence], axis=1) * 0.03
        return dry + wet

    def process_wide(self, dry: np.ndarray) -> np.ndarray:
        side = 0.5 * (dry[:, 0] - dry[:, 1])
        b, a = signal.butter(1, 160.0 / (self.sr / 2.0), btype="high")
        side_hp = signal.lfilter(b, a, side)
        wet = np.stack([side_hp, -side_hp], axis=1) * 0.12
        return dry + wet

    def process_deep(self, dry: np.ndarray) -> np.ndarray:
        delay_samples = int(self.sr * 0.010)
        delayed = self.zero_pad_delay(dry, delay_samples)
        dark_b, dark_a = signal.butter(1, 4200 / (self.sr / 2.0), btype="low")
        dark_l = signal.lfilter(dark_b, dark_a, delayed[:, 0])
        dark_r = signal.lfilter(dark_b, dark_a, delayed[:, 1])
        wet = np.stack([dark_l, dark_r], axis=1) * 0.16

        side = 0.5 * (dry[:, 0] - dry[:, 1])
        mono_like = float(np.mean(np.abs(side))) < 1e-5
        if mono_like:
            wet = self.force_pseudo_stereo(wet, delay_ms=0.30, blend=0.08)

        return dry + wet

    def process(
        self,
        x: np.ndarray,
        preset: str = "WIDE",
    ) -> tuple[np.ndarray, Dict[str, float]]:
        dry = self.ensure_stereo(np.asarray(x, dtype=np.float32))

        preset_key = preset.upper()
        if preset_key == "ORIGINAL":
            processed = self.process_original(dry)
        elif preset_key == "ZOOM":
            processed = self.process_zoom(dry)
        elif preset_key == "WIDE":
            processed = self.process_wide(dry)
        elif preset_key == "DEEP":
            processed = self.process_deep(dry)
        else:
            raise ValueError(f"Unknown preset: {preset}")

        if preset_key == "ORIGINAL":
            return processed, {"safety_gain_db": 0.0}

        safe, gain_db = self.safe_peak_scale(processed)
        return safe, {"safety_gain_db": float(gain_db)}
