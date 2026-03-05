import os
import glob
import numpy as np
import soundfile as sf
from scipy import signal


class V3DBinauralEngine:

    def __init__(self, sr=48000):
        self.sr = sr

    def ensure_stereo(self, x):
        if x.ndim == 1:
            return np.stack([x, x], axis=1)
        if x.shape[1] == 1:
            return np.concatenate([x, x], axis=1)
        return x[:, :2]

    def pseudo_stereo(self, x, delay_ms=0.3):
        delay_samples = int(self.sr * delay_ms / 1000)

        L = x[:, 0]
        R = np.roll(x[:, 1], delay_samples)

        return np.stack([L, R], axis=1)

    def wide(self, x):
        L = x[:, 0]
        R = x[:, 1]

        mid = (L + R) * 0.5
        side = (L - R) * 0.5

        side *= 1.5

        L2 = mid + side
        R2 = mid - side

        return np.stack([L2, R2], axis=1)

    def rear(self, x):

        delay_ms = 12
        delay_samples = int(self.sr * delay_ms / 1000)

        pad = np.zeros((delay_samples, 2))
        x = np.concatenate([pad, x[:-delay_samples]])

        b, a = signal.butter(1, 4000/(self.sr/2), "low")

        x[:,0] = signal.lfilter(b,a,x[:,0])
        x[:,1] = signal.lfilter(b,a,x[:,1])

        x *= 0.7

        return x

    def process(self, x, mode="wide"):

        x = self.ensure_stereo(x)

        x = self.pseudo_stereo(x)

        if mode == "wide":
            return self.wide(x)

        if mode == "rear":
            return self.rear(x)

        return x


def process_file(infile, outfile, mode):

    x, sr = sf.read(infile)

    engine = V3DBinauralEngine(sr)

    y = engine.process(x, mode)

    sf.write(outfile, y, sr)


def batch():

    files = glob.glob("input/*.wav")

    os.makedirs("output", exist_ok=True)

    for f in files:

        name = os.path.basename(f)

        process_file(
            f,
            f"output/wide_{name}",
            "wide"
        )

        process_file(
            f,
            f"output/rear_{name}",
            "rear"
        )


if __name__ == "__main__":

    batch()
