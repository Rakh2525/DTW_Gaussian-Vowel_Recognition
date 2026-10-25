"""
Extra experiments that back the analysis section of the report.

1. Averaged template vs single-recording template (DTW)
2. Sensitivity of the averaged template to the reference recording order
3. Covariance size (log-determinant) of each Gaussian vowel model

Usage: python analysis.py   (after python prepareDataset.py)
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np

import accuracyScoring as scoring
from DTW_Generalized import VOWELS, build_all_templates, recognize
from extraction import extract_mfcc_39
from Gaussian import build_all_models
from main import by_vowel, load_split

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def dtw_accuracy(speakers, train, tests):
    """Template built from `speakers` (in that order); accuracy on each test set."""
    templates = build_all_templates(by_vowel(train, speakers))
    out = []
    for test in tests:
        results = [
            (spk, vowel, recognize(audio, rate, templates)[0])
            for (spk, vowel), (audio, rate) in test.items()
        ]
        out.append(scoring.accuracy(results))
    return out


def main() -> None:
    train = load_split("template")
    closed = load_split("test/closed")
    open_ = load_split("test/open")
    speakers = sorted({s for s, _ in train})
    lines = []

    lines += ["## A. Averaged template vs template tunggal (DTW)", "",
              "| Template | Closed Speakers (%) | Open Speakers (%) |", "|---|---|---|"]
    avg = dtw_accuracy(speakers, train, [closed, open_])
    lines.append(f"| Averaged (3 speaker) | {avg[0]:.1f} | {avg[1]:.1f} |")
    singles = []
    for spk in speakers:
        acc = dtw_accuracy([spk], train, [closed, open_])
        singles.append(acc)
        lines.append(f"| Tunggal {spk} | {acc[0]:.1f} | {acc[1]:.1f} |")
    mean_single = np.mean(singles, axis=0)
    lines.append(f"| Rata-rata tunggal | {mean_single[0]:.1f} | {mean_single[1]:.1f} |")

    lines += ["", "## B. Pengaruh urutan rekaman referensi pada averaged template", "",
              "| Urutan (referensi pertama) | Closed Speakers (%) | Open Speakers (%) |", "|---|---|---|"]
    accs = []
    for order in itertools.permutations(speakers):
        acc = dtw_accuracy(list(order), train, [closed, open_])
        accs.append(acc)
        lines.append(f"| {' > '.join(order)} | {acc[0]:.1f} | {acc[1]:.1f} |")
    accs = np.array(accs)
    lines.append(f"| Rentang (min-maks) | {accs[:,0].min():.1f}-{accs[:,0].max():.1f} | {accs[:,1].min():.1f}-{accs[:,1].max():.1f} |")

    lines += ["", "## C. Ukuran covariance model Gaussian per vowel", "",
              "| Vowel | log-determinan covariance | jumlah frame latih |", "|---|---|---|"]
    models = build_all_models(by_vowel(train, speakers))
    for v in VOWELS:
        frames = sum(len(extract_mfcc_39(*train[(s, v)])) for s in speakers)
        lines.append(f"| /{v}/ | {models[v].log_det_covariance:.1f} | {frames} |")

    report = "\n".join(lines)
    print(report)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "analysis.md").write_text(report + "\n")


if __name__ == "__main__":
    main()
