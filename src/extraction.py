"""
using python_speech_features mfcc to extract processed audio for ASR
"""

import numpy as np
from python_speech_features import mfcc

FeatureSequence = np.ndarray


def compute_delta(features: np.ndarray, width: int = 2) -> np.ndarray:
    """Calculate temporal derivatives with the same shape as the input."""
    features = np.asarray(features, dtype=np.float64)

    if features.ndim != 2:
        raise ValueError("features must have shape (frames, coefficients)")

    if features.shape[0] == 0:
        raise ValueError("features must contain at least one frame")

    denominator = 2 * sum(index * index for index in range(1, width + 1))

    padded = np.pad(
        features,
        pad_width=((width, width), (0, 0)),
        mode="edge",
    )

    delta = np.zeros_like(features)

    for index in range(1, width + 1):
        forward = padded[width + index: width + index + len(features)]
        backward = padded[width - index: width - index + len(features)]
        delta += index * (forward - backward)

    return delta / denominator


def extract_mfcc_39(
    audio: np.ndarray,
    sample_rate: int,
) -> FeatureSequence:
    """Extract one 39-dimensional vector for every frame."""
    audio = np.asarray(audio)

    if audio.ndim != 1:
        raise ValueError("audio must be a mono one-dimensional signal")

    if audio.size == 0:
        raise ValueError("audio must not be empty")

    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    static_mfcc = mfcc(
        signal=audio.astype(np.float64),
        samplerate=sample_rate,
        winlen=0.025,
        winstep=0.010,
        numcep=13,
        nfilt=26,
        nfft=512,
        appendEnergy=True,
    )

    delta = compute_delta(static_mfcc)
    delta_delta = compute_delta(delta)

    features_39 = np.concatenate(
        (static_mfcc, delta, delta_delta),
        axis=1,
    )

    if features_39.shape[1] != 39:
        raise RuntimeError(
            f"Expected 39 features per frame, got {features_39.shape[1]}"
        )

    return features_39
