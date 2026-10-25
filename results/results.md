## Tabel 1. Akurasi (%)

| Sistem | Closed Recording | Closed Speakers | Open Speakers | Rata-rata |
|---|---|---|---|---|
| DTW Template | 100.0 | 86.7 | 70.2 | 85.6 |
| Model Gaussian | 100.0 | 93.3 | 58.3 | 83.9 |

## Tabel 2. Akurasi per vowel (%)

| Sistem | Skenario | /a/ | /i/ | /u/ | /e/ | /o/ |
|---|---|---|---|---|---|---|
| DTW Template | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| DTW Template | Closed Speakers | 100.0 | 100.0 | 66.7 | 100.0 | 66.7 |
| DTW Template | Open Speakers | 100.0 | 82.4 | 58.8 | 43.8 | 64.7 |
| DTW Template | Open (LOSO) | 100.0 | 66.7 | 33.3 | 100.0 | 33.3 |
| Model Gaussian | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Closed Speakers | 66.7 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Open Speakers | 52.9 | 100.0 | 35.3 | 31.2 | 70.6 |
| Model Gaussian | Open (LOSO) | 50.0 | 100.0 | 0.0 | 33.3 | 33.3 |

## Tabel 3. Akurasi per speaker (%)

| Sistem | Skenario | Speaker | Akurasi |
|---|---|---|---|
| DTW Template | Closed Recording | spk1 | 100.0 |
| DTW Template | Closed Recording | spk2 | 100.0 |
| DTW Template | Closed Recording | spk3 | 100.0 |
| DTW Template | Closed Speakers | spk1 | 100.0 |
| DTW Template | Closed Speakers | spk2 | 100.0 |
| DTW Template | Closed Speakers | spk3 | 60.0 |
| DTW Template | Open Speakers | G04_S03 | 40.0 |
| DTW Template | Open Speakers | G04_S04 | 40.0 |
| DTW Template | Open Speakers | G05_S01 | 60.0 |
| DTW Template | Open Speakers | G05_S02 | 80.0 |
| DTW Template | Open Speakers | G05_S03 | 60.0 |
| DTW Template | Open Speakers | G05_S04 | 80.0 |
| DTW Template | Open Speakers | G05_S05 | 100.0 |
| DTW Template | Open Speakers | G07_S01 | 60.0 |
| DTW Template | Open Speakers | G07_S02 | 20.0 |
| DTW Template | Open Speakers | G07_S03 | 100.0 |
| DTW Template | Open Speakers | G07_S04 | 100.0 |
| DTW Template | Open Speakers | G07_S05 | 40.0 |
| DTW Template | Open Speakers | G11_S01 | 40.0 |
| DTW Template | Open Speakers | G11_S02 | 100.0 |
| DTW Template | Open Speakers | G11_S03 | 100.0 |
| DTW Template | Open Speakers | G11_S04 | 80.0 |
| DTW Template | Open Speakers | G11_S05 | 100.0 |
| DTW Template | Open (LOSO) | spk1 | 60.0 |
| DTW Template | Open (LOSO) | spk2 | 60.0 |
| DTW Template | Open (LOSO) | spk3 | 80.0 |
| Model Gaussian | Closed Recording | spk1 | 100.0 |
| Model Gaussian | Closed Recording | spk2 | 100.0 |
| Model Gaussian | Closed Recording | spk3 | 100.0 |
| Model Gaussian | Closed Speakers | spk1 | 80.0 |
| Model Gaussian | Closed Speakers | spk2 | 100.0 |
| Model Gaussian | Closed Speakers | spk3 | 100.0 |
| Model Gaussian | Open Speakers | G04_S03 | 40.0 |
| Model Gaussian | Open Speakers | G04_S04 | 20.0 |
| Model Gaussian | Open Speakers | G05_S01 | 40.0 |
| Model Gaussian | Open Speakers | G05_S02 | 40.0 |
| Model Gaussian | Open Speakers | G05_S03 | 60.0 |
| Model Gaussian | Open Speakers | G05_S04 | 60.0 |
| Model Gaussian | Open Speakers | G05_S05 | 75.0 |
| Model Gaussian | Open Speakers | G07_S01 | 60.0 |
| Model Gaussian | Open Speakers | G07_S02 | 20.0 |
| Model Gaussian | Open Speakers | G07_S03 | 100.0 |
| Model Gaussian | Open Speakers | G07_S04 | 100.0 |
| Model Gaussian | Open Speakers | G07_S05 | 40.0 |
| Model Gaussian | Open Speakers | G11_S01 | 60.0 |
| Model Gaussian | Open Speakers | G11_S02 | 100.0 |
| Model Gaussian | Open Speakers | G11_S03 | 80.0 |
| Model Gaussian | Open Speakers | G11_S04 | 60.0 |
| Model Gaussian | Open Speakers | G11_S05 | 40.0 |
| Model Gaussian | Open (LOSO) | spk1 | 40.0 |
| Model Gaussian | Open (LOSO) | spk2 | 20.0 |
| Model Gaussian | Open (LOSO) | spk3 | 70.0 |

## Confusion matrix (baris = benar, kolom = prediksi)

**DTW Template - Closed Recording**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 3 | 0 | 0 | 0 | 0 |
| i | 0 | 3 | 0 | 0 | 0 |
| u | 0 | 0 | 3 | 0 | 0 |
| e | 0 | 0 | 0 | 3 | 0 |
| o | 0 | 0 | 0 | 0 | 3 |

**DTW Template - Closed Speakers**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 3 | 0 | 0 | 0 | 0 |
| i | 0 | 3 | 0 | 0 | 0 |
| u | 0 | 0 | 2 | 0 | 1 |
| e | 0 | 0 | 0 | 3 | 0 |
| o | 0 | 0 | 1 | 0 | 2 |

**DTW Template - Open Speakers**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 17 | 0 | 0 | 0 | 0 |
| i | 0 | 14 | 1 | 0 | 2 |
| u | 0 | 1 | 10 | 0 | 6 |
| e | 2 | 4 | 2 | 7 | 1 |
| o | 4 | 1 | 1 | 0 | 11 |

**DTW Template - Open (LOSO)**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 6 | 0 | 0 | 0 | 0 |
| i | 0 | 4 | 2 | 0 | 0 |
| u | 0 | 1 | 2 | 0 | 3 |
| e | 0 | 0 | 0 | 6 | 0 |
| o | 2 | 0 | 2 | 0 | 2 |

**Model Gaussian - Closed Recording**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 3 | 0 | 0 | 0 | 0 |
| i | 0 | 3 | 0 | 0 | 0 |
| u | 0 | 0 | 3 | 0 | 0 |
| e | 0 | 0 | 0 | 3 | 0 |
| o | 0 | 0 | 0 | 0 | 3 |

**Model Gaussian - Closed Speakers**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 2 | 1 | 0 | 0 | 0 |
| i | 0 | 3 | 0 | 0 | 0 |
| u | 0 | 0 | 3 | 0 | 0 |
| e | 0 | 0 | 0 | 3 | 0 |
| o | 0 | 0 | 0 | 0 | 3 |

**Model Gaussian - Open Speakers**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 9 | 6 | 0 | 0 | 2 |
| i | 0 | 17 | 0 | 0 | 0 |
| u | 0 | 5 | 6 | 0 | 6 |
| e | 0 | 10 | 1 | 5 | 0 |
| o | 4 | 1 | 0 | 0 | 12 |

**Model Gaussian - Open (LOSO)**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 3 | 3 | 0 | 0 | 0 |
| i | 0 | 6 | 0 | 0 | 0 |
| u | 0 | 4 | 0 | 0 | 2 |
| e | 0 | 4 | 0 | 2 | 0 |
| o | 1 | 3 | 0 | 0 | 2 |
