# DTW_Gaussian-Vowel_Recognition
Vowel recognition (/a i u e o/) with DTW averaged templates and Gaussian models.

## Run
```bash
pip install -r requirement.txt
python src/prepareDataset.py   # raw wavs -> data/template, data/test/closed
python src/main.py             # prints Tables 1-3, writes results/
```

## Pipeline
- `audioProcessing.py` load, mono, 16 kHz, silence trimming
- `extraction.py` MFCC 13 + delta + delta-delta = 39 dims (25 ms / 10 ms)
- `DTW_Generalized.py` DTW, averaged template (DTW-aligned mean), recognition
- `Gaussian.py` mean + full covariance per vowel, negative log-likelihood
- `accuracyScoring.py` accuracy overall / per vowel / per speaker, confusion matrix

## Scenarios (3 speakers)
- Closed recordings: test = recording 1 (used for template/model)
- Closed speakers: test = recording 2 of the same speakers
- Open speakers: `data/test/open/<vowel>/G??_S0x_<V>.wav`, 17 speakers from groups G04, G05, G07, G11 (84 recordings)
- Open (LOSO): extra check, leave-one-speaker-out inside our own group

## Dataset
- `data/template/`, `data/test/closed/`: our group (G06), speakers spk1-spk3
- `data/test/open/`: recordings of groups G04, G05, G07, G11, downloaded from the shared "Speech Open Set" Drive folder

## Tests
```bash
python -m unittest discover -s test -v
```

## Extra analysis
```bash
python src/analysis.py   # averaged vs single template, reference order, covariance size -> results/analysis.md
```
