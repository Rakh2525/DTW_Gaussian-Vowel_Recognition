"""
Unit tests. Run from the repo root:  python -m unittest discover -s test -v
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import accuracyScoring as scoring
from audioProcessing import (
    AudioProcessingError,
    convert_to_mono,
    normalize_audio,
    remove_silence,
    resample_audio,
    validate_audio,
)
from DTW_Generalized import (
    VOWELS,
    build_all_templates,
    calculate_dtw,
    create_averaged_template,
    euclidean_distance,
    recognize,
)
from extraction import compute_delta, extract_mfcc_39
from Gaussian import (
    build_all_models,
    fit_gaussian,
    negative_log_likelihood,
    recognize_gaussian,
)

RATE = 16000


def tone(freqs, seconds=0.5, seed=0):
    """Synthetic vowel-like signal: harmonics at freqs plus a little noise."""
    t = np.arange(int(RATE * seconds)) / RATE
    rng = np.random.default_rng(seed)
    signal = sum(np.sin(2 * np.pi * f * t) for f in freqs)
    return 0.3 * signal / len(freqs) + 0.001 * rng.standard_normal(t.size)


# Distinct formant-like spectra for the five classes
SPECTRA = {
    "a": (700, 1200),
    "i": (300, 2300),
    "u": (320, 800),
    "e": (500, 1900),
    "o": (500, 900),
}


class AudioProcessingTests(unittest.TestCase):
    def test_mono_averages_channels(self):
        stereo = np.array([[1.0, 3.0], [2.0, 4.0]])
        np.testing.assert_allclose(convert_to_mono(stereo), [2.0, 3.0])

    def test_mono_passthrough(self):
        x = np.arange(5.0)
        np.testing.assert_array_equal(convert_to_mono(x), x)

    def test_normalize_int16_range(self):
        x = np.array([-32768, 0, 32767], dtype=np.int16)
        y = normalize_audio(x)
        self.assertEqual(y.dtype, np.float64)
        self.assertLessEqual(np.abs(y).max(), 1.0)
        self.assertEqual(y[1], 0.0)

    def test_normalize_rejects_empty_and_nan(self):
        with self.assertRaises(AudioProcessingError):
            normalize_audio(np.array([]))
        with self.assertRaises(AudioProcessingError):
            normalize_audio(np.array([1.0, np.nan]))

    def test_resample_length_and_rate(self):
        x = np.random.default_rng(1).standard_normal(48000)
        y, rate = resample_audio(x, 48000, 16000)
        self.assertEqual(rate, 16000)
        self.assertEqual(len(y), 16000)

    def test_resample_same_rate_is_copy(self):
        x = np.arange(10.0)
        y, rate = resample_audio(x, 16000, 16000)
        np.testing.assert_array_equal(x, y)
        self.assertIsNot(x, y)

    def test_remove_silence_trims_edges(self):
        sound = tone((500,), seconds=0.3)
        padded = np.concatenate([np.zeros(RATE // 2), sound, np.zeros(RATE // 2)])
        trimmed = remove_silence(padded, RATE, threshold=0.01)
        self.assertLess(len(trimmed), len(padded))
        self.assertGreater(len(trimmed), len(sound) * 0.9)

    def test_remove_silence_all_silent_raises(self):
        with self.assertRaises(AudioProcessingError):
            remove_silence(np.zeros(RATE), RATE)

    def test_validate_rejects_wrong_rate_and_short(self):
        with self.assertRaises(AudioProcessingError):
            validate_audio(np.ones(RATE), 8000)
        with self.assertRaises(AudioProcessingError):
            validate_audio(np.ones(100), RATE)


class ExtractionTests(unittest.TestCase):
    def test_mfcc_is_39_dimensional(self):
        feats = extract_mfcc_39(tone((500, 1500)), RATE)
        self.assertEqual(feats.ndim, 2)
        self.assertEqual(feats.shape[1], 39)
        self.assertTrue(np.all(np.isfinite(feats)))

    def test_frame_count_matches_25ms_10ms(self):
        feats = extract_mfcc_39(tone((500,), seconds=1.0), RATE)
        expected = 1 + int(np.ceil((RATE - 400) / 160))
        self.assertEqual(feats.shape[0], expected)

    def test_mfcc_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            extract_mfcc_39(np.zeros((2, 100)), RATE)
        with self.assertRaises(ValueError):
            extract_mfcc_39(np.array([]), RATE)

    def test_delta_of_linear_ramp_is_constant(self):
        ramp = np.arange(20, dtype=float)[:, None] * np.ones((1, 3))
        delta = compute_delta(ramp)
        np.testing.assert_allclose(delta[3:-3], 1.0)
        self.assertEqual(delta.shape, ramp.shape)


class DTWTests(unittest.TestCase):
    def test_euclidean_distance(self):
        a, b = np.zeros(39), np.zeros(39)
        b[0] = 3.0
        b[1] = 4.0
        self.assertAlmostEqual(euclidean_distance(a, b), 5.0)
        with self.assertRaises(ValueError):
            euclidean_distance(np.zeros(3), np.zeros(3))

    def test_identical_sequences_cost_zero_diagonal_path(self):
        f = extract_mfcc_39(tone((500, 1500)), RATE)
        raw, norm, path = calculate_dtw(f, f)
        self.assertAlmostEqual(raw, 0.0)
        self.assertAlmostEqual(norm, 0.0)
        self.assertEqual(path, [(i, i) for i in range(len(f))])

    def test_dtw_is_symmetric_in_cost(self):
        a = extract_mfcc_39(tone((500, 1500)), RATE)
        b = extract_mfcc_39(tone((700, 1200), seconds=0.7), RATE)
        self.assertAlmostEqual(
            calculate_dtw(a, b)[0], calculate_dtw(b, a)[0], places=6
        )

    def test_dtw_handles_time_stretch_better_than_other_class(self):
        base = tone((500, 1500), seconds=0.4)
        slow = tone((500, 1500), seconds=0.8, seed=1)
        other = tone((300, 2300), seconds=0.8, seed=2)
        f = extract_mfcc_39(base, RATE)
        same = calculate_dtw(extract_mfcc_39(slow, RATE), f)[1]
        diff = calculate_dtw(extract_mfcc_39(other, RATE), f)[1]
        self.assertLess(same, diff)

    def test_path_is_monotonic_and_covers_ends(self):
        a = extract_mfcc_39(tone((500,), seconds=0.4), RATE)
        b = extract_mfcc_39(tone((900,), seconds=0.6), RATE)
        _, _, path = calculate_dtw(a, b)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (len(a) - 1, len(b) - 1))
        for (i0, j0), (i1, j1) in zip(path, path[1:]):
            self.assertIn((i1 - i0, j1 - j0), [(1, 0), (0, 1), (1, 1)])

    def test_averaged_template_has_reference_length(self):
        seqs = [
            extract_mfcc_39(tone((500, 1500), seconds=s, seed=i), RATE)
            for i, s in enumerate((0.4, 0.5, 0.6))
        ]
        avg = create_averaged_template(seqs)
        self.assertEqual(avg.shape, seqs[0].shape)

    def test_averaged_template_of_single_sequence_is_itself(self):
        f = extract_mfcc_39(tone((500,)), RATE)
        np.testing.assert_allclose(create_averaged_template([f]), f)

    def test_averaged_template_requires_input(self):
        with self.assertRaises(ValueError):
            create_averaged_template([])


def make_recordings(per_vowel=3):
    return {
        v: [(tone(SPECTRA[v], seed=10 * k + i), RATE) for k in range(per_vowel)
            for i in [VOWELS.index(v)]]
        for v in VOWELS
    }


class RecognitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train = make_recordings()
        cls.templates = build_all_templates(cls.train)
        cls.models = build_all_models(cls.train)

    def test_dtw_recognises_synthetic_vowels(self):
        for v in VOWELS:
            audio = tone(SPECTRA[v], seed=99)
            predicted, costs = recognize(audio, RATE, self.templates)
            self.assertEqual(predicted, v)
            self.assertEqual(set(costs), set(VOWELS))

    def test_gaussian_recognises_synthetic_vowels(self):
        for v in VOWELS:
            audio = tone(SPECTRA[v], seed=99)
            predicted, _ = recognize_gaussian(audio, RATE, self.models)
            self.assertEqual(predicted, v)

    def test_missing_vowel_raises(self):
        incomplete = {v: r for v, r in self.train.items() if v != "a"}
        with self.assertRaises(ValueError):
            build_all_templates(incomplete)
        with self.assertRaises(ValueError):
            build_all_models(incomplete)


class GaussianTests(unittest.TestCase):
    def test_fit_recovers_mean_and_covariance(self):
        rng = np.random.default_rng(0)
        cov = np.diag(np.linspace(0.5, 2.0, 39))
        frames = rng.multivariate_normal(np.ones(39), cov, size=20000)
        model = fit_gaussian([frames])
        np.testing.assert_allclose(model.mean, 1.0, atol=0.05)
        np.testing.assert_allclose(
            np.diag(model.covariance), np.diag(cov), atol=0.1
        )

    def test_nll_matches_scipy_style_formula(self):
        rng = np.random.default_rng(1)
        frames = rng.standard_normal((500, 39))
        model = fit_gaussian([frames])
        x = rng.standard_normal((10, 39))
        d = x - model.mean
        expected = np.mean(
            0.5
            * (
                39 * np.log(2 * np.pi)
                + np.linalg.slogdet(model.covariance)[1]
                + np.einsum("ij,jk,ik->i", d, np.linalg.inv(model.covariance), d)
            )
        )
        self.assertAlmostEqual(negative_log_likelihood(x, model), expected, places=6)

    def test_nll_lower_for_own_distribution(self):
        rng = np.random.default_rng(2)
        own = rng.standard_normal((400, 39))
        other = rng.standard_normal((400, 39)) + 5.0
        model = fit_gaussian([own])
        self.assertLess(
            negative_log_likelihood(own[:50], model),
            negative_log_likelihood(other[:50], model),
        )

    def test_covariance_is_symmetric_positive_definite(self):
        frames = np.random.default_rng(3).standard_normal((60, 39))
        model = fit_gaussian([frames])
        np.testing.assert_allclose(model.covariance, model.covariance.T)
        self.assertTrue(np.all(np.linalg.eigvalsh(model.covariance) > 0))

    def test_fit_rejects_empty_and_bad_shape(self):
        with self.assertRaises(ValueError):
            fit_gaussian([])
        with self.assertRaises(ValueError):
            fit_gaussian([np.zeros((10, 5))])


class ScoringTests(unittest.TestCase):
    RESULTS = [
        ("s1", "a", "a"),
        ("s1", "i", "u"),
        ("s2", "a", "a"),
        ("s2", "u", "u"),
    ]

    def test_overall_accuracy(self):
        self.assertAlmostEqual(scoring.accuracy(self.RESULTS), 75.0)

    def test_empty_accuracy_is_nan(self):
        self.assertTrue(np.isnan(scoring.accuracy([])))

    def test_per_vowel(self):
        per = scoring.accuracy_per_vowel(self.RESULTS)
        self.assertEqual(per["a"], 100.0)
        self.assertEqual(per["i"], 0.0)
        self.assertEqual(per["u"], 100.0)
        self.assertTrue(np.isnan(per["e"]))

    def test_per_speaker(self):
        per = scoring.accuracy_per_speaker(self.RESULTS)
        self.assertEqual(per, {"s1": 50.0, "s2": 100.0})

    def test_confusion_matrix(self):
        m = scoring.confusion_matrix(self.RESULTS)
        self.assertEqual(m["a"]["a"], 2)
        self.assertEqual(m["i"]["u"], 1)
        self.assertEqual(sum(sum(r.values()) for r in m.values()), 4)


if __name__ == "__main__":
    unittest.main()
