"""
Accuracy scoring: overall, per vowel, per speaker and confusion matrix.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from DTW_Generalized import VOWELS

# One result is (speaker, true_vowel, predicted_vowel)
Result = tuple[str, str, str]


def accuracy(results: Sequence[Result]) -> float:
    """Accuracy = correct predictions / all test data x 100."""
    if not results:
        return float("nan")
    correct = sum(1 for _, true, pred in results if true == pred)
    return correct / len(results) * 100.0


def accuracy_per_vowel(results: Sequence[Result]) -> dict[str, float]:
    return {
        vowel: accuracy([r for r in results if r[1] == vowel])
        for vowel in VOWELS
    }


def accuracy_per_speaker(results: Sequence[Result]) -> dict[str, float]:
    speakers = sorted({r[0] for r in results})
    return {
        speaker: accuracy([r for r in results if r[0] == speaker])
        for speaker in speakers
    }


def confusion_matrix(results: Sequence[Result]) -> dict[str, dict[str, int]]:
    """matrix[true][predicted] = count"""
    matrix: dict[str, dict[str, int]] = {
        true: defaultdict(int) for true in VOWELS
    }
    for _, true, pred in results:
        matrix[true][pred] += 1
    return {
        true: {pred: matrix[true][pred] for pred in VOWELS}
        for true in VOWELS
    }
