from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
from scipy import signal


@dataclass(frozen=True)
class ProcessMetadata:
    safety_gain_db: float


class V3DEngine:
    """V6.0b1 Depth & Body engine for mobile-video stereo sources."""

    def __init__(self, sr: int = 48000) -> None:
        self.sr = sr

    def ensure_stereo(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            return np.stack([x, x], axis=1)
        if x.shape[1] == 1:
            return np.concatenate([x, x], axis=1)
        return x[:, :2]

    def safe_peak_scale(self, x: np.ndarray, headroom_db: float = -1.0) -> tuple[np.ndarray, float]:
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

    def force_pseudo_stereo(self, x: np.ndarray, delay_ms: float = 0.25, blend: float = 0.18) -> np.ndarray:
        delay_samples = max(1, int(self.sr * delay_ms / 1000.0))
        delayed_l = self.zero_pad_delay(x[:, [0]], delay_samples)[:, 0]
        delayed_r = self.zero_pad_delay(x[:, [1]], delay_samples)[:, 0]

        out_l = (1.0 - blend) * x[:, 0] + blend * delayed_r
        out_r = (1.0 - blend) * x[:, 1] + blend * delayed_l
        return np.stack([out_l, out_r], axis=1)

    def process_zoom(self, x: np.ndarray) -> np.ndarray:
        l, r = x[:, 0], x[:, 1]
        mid = 0.5 * (l + r)
        side = 0.5 * (l - r)

        side *= 0.95
        b, a = signal.butter(1, 3800 / (self.sr / 2.0), btype="high")
        presence = signal.lfilter(b, a, mid) * 0.04

        out_l = mid + side + presence
        out_r = mid - side + presence
        return np.stack([out_l, out_r], axis=1)

    def process_wide(self, x: np.ndarray) -> np.ndarray:
        l, r = x[:, 0], x[:, 1]
        mid = 0.5 * (l + r)
        side = 0.5 * (l - r)
        side *= 1.28

        body = signal.lfilter(*signal.butter(1, 180 / (self.sr / 2.0), btype="low"), mid) * 0.08

        out_l = mid + side + body
        out_r = mid - side + body
        return np.stack([out_l, out_r], axis=1)

    def process_deep(self, x: np.ndarray) -> np.ndarray:
        delay_samples = int(self.sr * 0.012)
        delayed = self.zero_pad_delay(x, delay_samples)

        b, a = signal.butter(1, 4200 / (self.sr / 2.0), btype="low")
        dark_l = signal.lfilter(b, a, delayed[:, 0])
        dark_r = signal.lfilter(b, a, delayed[:, 1])

        out = np.stack([dark_l, dark_r], axis=1) * 0.86
        dry = x * 0.16
        return out + dry

    def process(self, x: np.ndarray, preset: str = "WIDE") -> tuple[np.ndarray, Dict[str, float]]:
        stereo = self.ensure_stereo(np.asarray(x, dtype=np.float32))
        pseudo = self.force_pseudo_stereo(stereo)

        preset_key = preset.upper()
        if preset_key == "ZOOM":
            processed = self.process_zoom(pseudo)
        elif preset_key == "WIDE":
            processed = self.process_wide(pseudo)
        elif preset_key == "DEEP":
            processed = self.process_deep(pseudo)
        else:
            raise ValueError(f"Unknown preset: {preset}")

        safe, gain_db = self.safe_peak_scale(processed)
        return safe, {"safety_gain_db": float(gain_db)}
