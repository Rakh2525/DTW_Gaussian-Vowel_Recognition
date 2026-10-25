# DTW_Gaussian-Vowel_Recognition
Vowel recognition (/a i u e o/) with DTW averaged templates and Gaussian models.

## Run
```bash
pip install -r requirement.txt
python src/prepareDataset.py   # raw wavs -> data/template, data/test_closed
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
- Open speakers: `data/test_open/<vowel>/G07_S0x_<V>.wav`, 5 speakers from another group (25 recordings)
- Open (LOSO): extra check, leave-one-speaker-out inside our own group
