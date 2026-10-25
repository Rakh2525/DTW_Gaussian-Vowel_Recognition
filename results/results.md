## Tabel 1. Akurasi (%)

| Sistem | Closed Recording | Closed Speakers | Open Speakers | Rata-rata |
|---|---|---|---|---|
| DTW Template | 100.0 | 86.7 | 64.0 | 83.6 |
| Model Gaussian | 100.0 | 93.3 | 64.0 | 85.8 |

## Tabel 2. Akurasi per vowel (%)

| Sistem | Skenario | /a/ | /i/ | /u/ | /e/ | /o/ |
|---|---|---|---|---|---|---|
| DTW Template | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| DTW Template | Closed Speakers | 100.0 | 100.0 | 66.7 | 100.0 | 66.7 |
| DTW Template | Open Speakers | 100.0 | 60.0 | 40.0 | 40.0 | 80.0 |
| DTW Template | Open (LOSO) | 100.0 | 66.7 | 33.3 | 100.0 | 33.3 |
| Model Gaussian | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Closed Speakers | 66.7 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Open Speakers | 60.0 | 100.0 | 40.0 | 40.0 | 80.0 |
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
| DTW Template | Open Speakers | G07_S01 | 60.0 |
| DTW Template | Open Speakers | G07_S02 | 20.0 |
| DTW Template | Open Speakers | G07_S03 | 100.0 |
| DTW Template | Open Speakers | G07_S04 | 100.0 |
| DTW Template | Open Speakers | G07_S05 | 40.0 |
| DTW Template | Open (LOSO) | spk1 | 60.0 |
| DTW Template | Open (LOSO) | spk2 | 60.0 |
| DTW Template | Open (LOSO) | spk3 | 80.0 |
| Model Gaussian | Closed Recording | spk1 | 100.0 |
| Model Gaussian | Closed Recording | spk2 | 100.0 |
| Model Gaussian | Closed Recording | spk3 | 100.0 |
| Model Gaussian | Closed Speakers | spk1 | 80.0 |
| Model Gaussian | Closed Speakers | spk2 | 100.0 |
| Model Gaussian | Closed Speakers | spk3 | 100.0 |
| Model Gaussian | Open Speakers | G07_S01 | 60.0 |
| Model Gaussian | Open Speakers | G07_S02 | 20.0 |
| Model Gaussian | Open Speakers | G07_S03 | 100.0 |
| Model Gaussian | Open Speakers | G07_S04 | 100.0 |
| Model Gaussian | Open Speakers | G07_S05 | 40.0 |
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
| a | 5 | 0 | 0 | 0 | 0 |
| i | 0 | 3 | 0 | 0 | 2 |
| u | 0 | 0 | 2 | 0 | 3 |
| e | 0 | 2 | 1 | 2 | 0 |
| o | 1 | 0 | 0 | 0 | 4 |

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
| a | 3 | 2 | 0 | 0 | 0 |
| i | 0 | 5 | 0 | 0 | 0 |
| u | 0 | 1 | 2 | 0 | 2 |
| e | 0 | 2 | 1 | 2 | 0 |
| o | 1 | 0 | 0 | 0 | 4 |

**Model Gaussian - Open (LOSO)**

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 3 | 3 | 0 | 0 | 0 |
| i | 0 | 6 | 0 | 0 | 0 |
| u | 0 | 4 | 0 | 0 | 2 |
| e | 0 | 4 | 0 | 2 | 0 |
| o | 1 | 3 | 0 | 0 | 2 |
