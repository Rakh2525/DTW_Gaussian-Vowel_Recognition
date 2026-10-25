"""
Run both vowel recognisers (DTW averaged template, Gaussian) on all
scenarios and print Tables 1-3 from the assignment.

Scenarios
- Closed recordings: test = the recordings used to build template/model.
- Closed speakers:   test = other recording of the same speakers.
- Open speakers:     data/test_open = recordings of other groups' speakers.
- Open (LOSO):       extra check, leave-one-speaker-out inside our own group.

Usage: python main.py   (after python prepareDataset.py)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import accuracyScoring as scoring
from audioProcessing import prepare_audio, remove_silence
from DTW_Generalized import VOWELS, build_all_templates, recognize
from Gaussian import build_all_models, recognize_gaussian

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
SILENCE_THRESHOLD = 0.02  # RMS, after peak normalisation


def load_recording(path: Path) -> tuple[np.ndarray, int]:
    """16 kHz mono, peak-normalised (mic gain differs per speaker), trimmed."""
    audio, rate = prepare_audio(path)
    audio = audio / np.max(np.abs(audio))
    audio = remove_silence(audio, rate, threshold=SILENCE_THRESHOLD)
    return audio, rate


def load_split(split: str) -> dict[tuple[str, str], tuple[np.ndarray, int]]:
    """{(speaker, vowel): (audio, rate)}"""
    return {
        (path.stem.removesuffix(f"_{vowel.upper()}"), vowel): load_recording(path)
        for vowel in VOWELS
        for path in sorted((DATA / split / vowel).glob("*.wav"))
    }


def by_vowel(recordings, speakers):
    return {
        vowel: [
            recordings[(speaker, vowel)] for speaker in speakers
        ]
        for vowel in VOWELS
    }


def evaluate(train, test):
    """Return (dtw_results, gaussian_results) for the given data."""
    speakers = sorted({speaker for speaker, _ in train})
    train_by_vowel = by_vowel(train, speakers)
    templates = build_all_templates(train_by_vowel)
    models = build_all_models(train_by_vowel)

    dtw_results, gauss_results = [], []
    for (speaker, vowel), (audio, rate) in test.items():
        dtw_results.append((speaker, vowel, recognize(audio, rate, templates)[0]))
        gauss_results.append(
            (speaker, vowel, recognize_gaussian(audio, rate, models)[0])
        )
    return dtw_results, gauss_results


def main() -> None:
    train = load_split("template")
    test_closed = load_split("test_closed")
    speakers = sorted({speaker for speaker, _ in train})

    scenarios: dict[str, dict[str, list]] = {"DTW": {}, "Gaussian": {}}

    def store(scenario, dtw, gauss):
        scenarios["DTW"][scenario] = dtw
        scenarios["Gaussian"][scenario] = gauss

    store("Closed Recording", *evaluate(train, train))
    store("Closed Speakers", *evaluate(train, test_closed))

    store("Open Speakers", *evaluate(train, load_split("test_open")))

    open_dtw, open_gauss = [], []
    for held_out in speakers:
        sub_train = {k: v for k, v in train.items() if k[0] != held_out}
        for source in (train, test_closed):
            part = {k: v for k, v in source.items() if k[0] == held_out}
            d, g = evaluate(sub_train, part)
            open_dtw += d
            open_gauss += g
    store("Open (LOSO)", open_dtw, open_gauss)

    names = {"DTW": "DTW Template", "Gaussian": "Model Gaussian"}
    order = ["Closed Recording", "Closed Speakers", "Open Speakers"]
    extra = ["Open (LOSO)"]
    lines = ["## Tabel 1. Akurasi (%)", "",
             "| Sistem | Closed Recording | Closed Speakers | Open Speakers | Rata-rata |",
             "|---|---|---|---|---|"]
    summary = {}
    for system in ("DTW", "Gaussian"):
        accs = [scoring.accuracy(scenarios[system][s]) for s in order]
        summary[system] = accs
        lines.append(
            f"| {names[system]} | "
            + " | ".join(f"{a:.1f}" for a in accs)
            + f" | {np.mean(accs):.1f} |"
        )

    lines += ["", "## Tabel 2. Akurasi per vowel (%)", "",
              "| Sistem | Skenario | " + " | ".join(f"/{v}/" for v in VOWELS) + " |",
              "|---|---|" + "---|" * len(VOWELS)]
    for system in ("DTW", "Gaussian"):
        for s in order + extra:
            per = scoring.accuracy_per_vowel(scenarios[system][s])
            lines.append(
                f"| {names[system]} | {s} | "
                + " | ".join(f"{per[v]:.1f}" for v in VOWELS) + " |"
            )

    lines += ["", "## Tabel 3. Akurasi per speaker (%)", "",
              "| Sistem | Skenario | Speaker | Akurasi |",
              "|---|---|---|---|"]
    for system in ("DTW", "Gaussian"):
        for s in order + extra:
            per = scoring.accuracy_per_speaker(scenarios[system][s])
            for sp, a in per.items():
                lines.append(f"| {names[system]} | {s} | {sp} | {a:.1f} |")

    lines += ["", "## Confusion matrix (baris = benar, kolom = prediksi)"]
    for system in ("DTW", "Gaussian"):
        for s in order + extra:
            matrix = scoring.confusion_matrix(scenarios[system][s])
            lines += ["", f"**{names[system]} - {s}**", "",
                      "| benar \\ prediksi | " + " | ".join(VOWELS) + " |",
                      "|---|" + "---|" * len(VOWELS)]
            for true in VOWELS:
                lines.append(
                    f"| {true} | " + " | ".join(str(matrix[true][p]) for p in VOWELS) + " |"
                )

    report = "\n".join(lines)
    print(report)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "results.md").write_text(report + "\n")
    (RESULTS / "predictions.json").write_text(
        json.dumps(scenarios, indent=1)
    )


if __name__ == "__main__":
    main()
