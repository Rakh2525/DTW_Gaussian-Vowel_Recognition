"""
DTW functions for DTW ASR
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
from python_speech_features import mfcc


VOWELS = ("a", "i", "u", "e", "o")
FeatureSequence = np.ndarray
Recording = tuple[np.ndarray, int]


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




def euclidean_distance(
    frame_a: np.ndarray,
    frame_b: np.ndarray,
) -> float:
    """Calculate the distance between two 39-dimensional frames."""
    frame_a = np.asarray(frame_a, dtype=np.float64)
    frame_b = np.asarray(frame_b, dtype=np.float64)

    if frame_a.shape != (39,) or frame_b.shape != (39,):
        raise ValueError("both frames must have shape (39,)")

    return float(np.linalg.norm(frame_a - frame_b))


def calculate_dtw(
    input_features: FeatureSequence,
    template_features: FeatureSequence,
) -> tuple[float, float, list[tuple[int, int]]]:
    """Calculate DTW cost and alignment path.

    Returns:
        raw_cost: Final accumulated DTW cost.
        normalized_cost: Cost divided by alignment path length.
        path: List of (input_frame_index, template_frame_index) pairs.
    """
    input_features = np.asarray(input_features, dtype=np.float64)
    template_features = np.asarray(template_features, dtype=np.float64)

    validate_feature_sequence(input_features)
    validate_feature_sequence(template_features)

    input_length = input_features.shape[0]
    template_length = template_features.shape[0]

    cost = np.full(
        (input_length, template_length),
        np.inf,
        dtype=np.float64,
    )

    cost[0, 0] = euclidean_distance(
        input_features[0],
        template_features[0],
    )

    for input_index in range(1, input_length):
        cost[input_index, 0] = (
            cost[input_index - 1, 0]
            + euclidean_distance(
                input_features[input_index],
                template_features[0],
            )
        )

    for template_index in range(1, template_length):
        cost[0, template_index] = (
            cost[0, template_index - 1]
            + euclidean_distance(
                input_features[0],
                template_features[template_index],
            )
        )

    for input_index in range(1, input_length):
        for template_index in range(1, template_length):
            local_cost = euclidean_distance(
                input_features[input_index],
                template_features[template_index],
            )

            previous_cost = min(
                cost[input_index - 1, template_index],
                cost[input_index, template_index - 1],
                cost[input_index - 1, template_index - 1],
            )

            cost[input_index, template_index] = (
                local_cost + previous_cost
            )

    path = backtrack_dtw_path(cost)

    raw_cost = float(cost[-1, -1])
    normalized_cost = raw_cost / len(path)

    return raw_cost, normalized_cost, path


def backtrack_dtw_path(
    cost: np.ndarray,
) -> list[tuple[int, int]]:
    """Recover the minimum-cost DTW path."""
    input_index = cost.shape[0] - 1
    template_index = cost.shape[1] - 1

    path = [(input_index, template_index)]

    while input_index > 0 or template_index > 0:
        candidates: list[tuple[float, int, int]] = []

        if input_index > 0:
            candidates.append(
                (
                    cost[input_index - 1, template_index],
                    input_index - 1,
                    template_index,
                )
            )

        if template_index > 0:
            candidates.append(
                (
                    cost[input_index, template_index - 1],
                    input_index,
                    template_index - 1,
                )
            )

        if input_index > 0 and template_index > 0:
            candidates.append(
                (
                    cost[input_index - 1, template_index - 1],
                    input_index - 1,
                    template_index - 1,
                )
            )

        _, input_index, template_index = min(candidates)
        path.append((input_index, template_index))

    path.reverse()
    return path


def create_averaged_template(
    feature_sequences: Sequence[FeatureSequence],
) -> FeatureSequence:
    """Create an averaged template using the first sequence as reference."""
    if not feature_sequences:
        raise ValueError("at least one feature sequence is required")

    validated_sequences = []

    for sequence in feature_sequences:
        sequence = np.asarray(sequence, dtype=np.float64)
        validate_feature_sequence(sequence)
        validated_sequences.append(sequence)

    reference = validated_sequences[0]
    aligned_frames: list[list[np.ndarray]] = [
        [reference[reference_index]]
        for reference_index in range(len(reference))
    ]

    for sequence in validated_sequences[1:]:
        _, _, path = calculate_dtw(sequence, reference)

        for sequence_index, reference_index in path:
            aligned_frames[reference_index].append(
                sequence[sequence_index]
            )

    return np.vstack(
        [
            np.mean(frames_for_reference, axis=0)
            for frames_for_reference in aligned_frames
        ]
    )


def build_all_templates(
    template_recordings: Mapping[str, Sequence[Recording]],
) -> dict[str, FeatureSequence]:
    """Build one averaged MFCC-39 template for each vowel."""
    templates: dict[str, FeatureSequence] = {}

    for vowel in VOWELS:
        if vowel not in template_recordings:
            raise ValueError(f"missing recordings for vowel {vowel!r}")

        recordings = template_recordings[vowel]

        if len(recordings) != 5:
            raise ValueError(
                f"vowel {vowel!r} must have exactly 5 template recordings"
            )

        feature_sequences = [
            extract_mfcc_39(audio, sample_rate)
            for audio, sample_rate in recordings
        ]

        templates[vowel] = create_averaged_template(feature_sequences)

    return templates


def recognize(
    test_audio: np.ndarray,
    sample_rate: int,
    templates: Mapping[str, FeatureSequence],
) -> tuple[str, dict[str, float]]:
    """Recognize a vowel using the smallest normalized DTW cost."""
    input_features = extract_mfcc_39(test_audio, sample_rate)
    costs: dict[str, float] = {}

    for vowel in VOWELS:
        if vowel not in templates:
            raise ValueError(f"missing template for vowel {vowel!r}")

        _, normalized_cost, _ = calculate_dtw(
            input_features,
            templates[vowel],
        )

        costs[vowel] = normalized_cost

    predicted_vowel = min(costs, key=costs.get)
    return predicted_vowel, costs


def validate_feature_sequence(features: np.ndarray) -> None:
    """Validate the shape of a sequence of MFCC-39 frames."""
    if features.ndim != 2:
        raise ValueError(
            "feature sequence must have shape (frames, 39)"
        )

    if features.shape[0] == 0:
        raise ValueError("feature sequence must contain at least one frame")

    if features.shape[1] != 39:
        raise ValueError(
            f"feature sequence must have 39 columns, got {features.shape[1]}"
        )