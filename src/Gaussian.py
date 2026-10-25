"""
Gaussian function for Gaussian ASR

One multivariate Gaussian (mean + full covariance) per vowel, fitted on all
MFCC-39 frames of that vowel's training recordings. An input is scored with
the average per-frame negative log-likelihood under each vowel's model and
the smallest value wins.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from extraction import FeatureSequence, extract_mfcc_39
from DTW_Generalized import VOWELS, Recording, validate_feature_sequence

# Ridge added to the covariance diagonal so it stays invertible when the
# number of training frames is small relative to the 39 dimensions.
COVARIANCE_RIDGE = 1e-3


@dataclass(frozen=True)
class GaussianModel:
    mean: np.ndarray
    covariance: np.ndarray
    inverse_covariance: np.ndarray
    log_det_covariance: float


def fit_gaussian(
    feature_sequences: Sequence[FeatureSequence],
    ridge: float = COVARIANCE_RIDGE,
) -> GaussianModel:
    """Estimate mean and covariance from the pooled frames."""
    if not feature_sequences:
        raise ValueError("at least one feature sequence is required")

    for sequence in feature_sequences:
        validate_feature_sequence(np.asarray(sequence))

    frames = np.vstack(feature_sequences).astype(np.float64)

    if frames.shape[0] < 2:
        raise ValueError("at least two frames are required")

    mean = frames.mean(axis=0)
    centered = frames - mean
    covariance = centered.T @ centered / (frames.shape[0] - 1)
    covariance += ridge * np.eye(covariance.shape[0])

    sign, log_det = np.linalg.slogdet(covariance)
    if sign <= 0:
        raise ValueError("covariance matrix is not positive definite")

    return GaussianModel(
        mean=mean,
        covariance=covariance,
        inverse_covariance=np.linalg.inv(covariance),
        log_det_covariance=float(log_det),
    )


def negative_log_likelihood(
    features: FeatureSequence,
    model: GaussianModel,
) -> float:
    """Average per-frame negative log-likelihood of features under model."""
    features = np.asarray(features, dtype=np.float64)
    validate_feature_sequence(features)

    dimension = features.shape[1]
    centered = features - model.mean
    mahalanobis = np.einsum(
        "ij,jk,ik->i", centered, model.inverse_covariance, centered
    )

    per_frame = 0.5 * (
        dimension * np.log(2.0 * np.pi)
        + model.log_det_covariance
        + mahalanobis
    )
    return float(per_frame.mean())


def build_all_models(
    template_recordings: Mapping[str, Sequence[Recording]],
) -> dict[str, GaussianModel]:
    """Fit one Gaussian per vowel from its training recordings."""
    models: dict[str, GaussianModel] = {}

    for vowel in VOWELS:
        if not template_recordings.get(vowel):
            raise ValueError(f"missing recordings for vowel {vowel!r}")

        feature_sequences = [
            extract_mfcc_39(audio, sample_rate)
            for audio, sample_rate in template_recordings[vowel]
        ]
        models[vowel] = fit_gaussian(feature_sequences)

    return models


def recognize_gaussian(
    test_audio: np.ndarray,
    sample_rate: int,
    models: Mapping[str, GaussianModel],
) -> tuple[str, dict[str, float]]:
    """Recognize a vowel using the smallest negative log-likelihood."""
    features = extract_mfcc_39(test_audio, sample_rate)
    costs = {
        vowel: negative_log_likelihood(features, models[vowel])
        for vowel in VOWELS
    }
    return min(costs, key=costs.get), costs
