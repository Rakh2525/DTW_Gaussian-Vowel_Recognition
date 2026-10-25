"""
Organise the raw group recordings into the dataset layout:

    data/template/<vowel>/<speaker>.wav     recording 1 (training)
    data/test_closed/<vowel>/<speaker>.wav  recording 2 (same speaker)

The open-speaker scenario is leave-one-speaker-out over this same data (see
main.py), so there is no separate test_open copy.

Usage: python prepareDataset.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# speaker -> (folder, filename for (vowel, recording_number))
SPEAKERS = {
    "spk1": (ROOT, lambda v, n: f"{v.upper()}{'' if n == 1 else 2}.wav"),
    "spk2": (
        ROOT / "drive-download-20261025T131640Z-1-001",
        lambda v, n: f"{v.upper()}{'' if n == 1 else 2}-1.wav",
    ),
    "spk3": (
        ROOT / "drive-download-20261025T131647Z-1-001",
        lambda v, n: f"G06_{v.upper()}_0{n}.wav",
    ),
}

VOWELS = ("a", "i", "u", "e", "o")


def main() -> None:
    for speaker, (folder, name_of) in SPEAKERS.items():
        for vowel in VOWELS:
            for number, split in ((1, "template"), (2, "test_closed")):
                source = folder / name_of(vowel, number)
                target = DATA / split / vowel / f"{speaker}.wav"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    print(f"dataset written to {DATA}")


if __name__ == "__main__":
    main()
