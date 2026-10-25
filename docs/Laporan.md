# Laporan Praktikum: Pengenalan Vowel Bahasa Indonesia dengan DTW dan Model Gaussian

Kelas Pemrosesan Ucapan, Minggu ke-9

> DRAFT. Bagian bertanda `[ISI]` perlu dilengkapi kelompok.

## 1. Identitas Kelompok

- Kelompok: G06
- Anggota:

| No | Nama | NIM |
|---|---|---|
| 1 | `[ISI]` | `[ISI]` |
| 2 | `[ISI]` | `[ISI]` |
| 3 | `[ISI]` | `[ISI]` |

Pada kode dan data, ketiga speaker kelompok dinamai `spk1`, `spk2`, `spk3` (spk1 adalah Aldoy, spk2 adalah Nadhif, dan spk3 adalah Rabbani).

## 2. Link Program

https://github.com/Rakh2525/DTW_Gaussian-Vowel_Recognition/tree/main/src

Cara menjalankan (dari root repository):

```bash
pip install -r requirement.txt
python src/prepareDataset.py   # rekaman mentah -> data/
python src/main.py             # Tabel 1-3 + confusion matrix -> results/
python -m unittest discover -s test -v   # 34 unit test
```

## 3. Link Data

https://github.com/Rakh2525/DTW_Gaussian-Vowel_Recognition/tree/main/data

(`[ISI: tambahkan link Google Drive bila ada]`)

| Folder | Isi | Jumlah |
|---|---|---|
| `data/template/<vowel>/` | rekaman 1 tiap speaker kelompok, dipakai membangun template dan model | 15 |
| `data/test_closed/<vowel>/` | rekaman 2 tiap speaker kelompok | 15 |
| `data/test_open/<vowel>/` | rekaman speaker dari kelompok lain (G04, G05, G07, G11), 17 speaker | 84 |

Rekaman open diambil dari folder Drive bersama "Speech Open Set". Satu rekaman (G05_S05, vowel /e/) tidak tersedia, sehingga jumlahnya 84, bukan 85. Rekaman kelompok kami direkam dengan sample rate dan perangkat berbeda (16 kHz dan 48 kHz), semuanya diubah ke 16 kHz mono.

## 4. Metode dan Implementasi

### 4.1 Preprocessing

1. Baca WAV, ubah ke float64 dan normalisasi ke [-1, 1].
2. Ubah ke mono (rata-rata kanal), resample ke 16 kHz.
3. Normalisasi amplitudo puncak per rekaman, karena gain mikrofon tiap speaker berbeda jauh.
4. Pangkas diam di awal dan akhir (RMS frame 25 ms, ambang 0,02 setelah normalisasi).

### 4.2 Ekstraksi fitur: MFCC 39 dimensi

`python_speech_features.mfcc` dengan jendela 25 ms, geser 10 ms, 13 koefisien (c0 diganti log-energi), 26 filter mel, NFFT 512. Ditambah delta dan delta-delta (dihitung sendiri, lebar 2), sehingga tiap frame berdimensi 13 + 13 + 13 = 39. Kode akan error bila dimensi bukan 39.

Tidak dilakukan CMVN per rekaman, karena rata-rata spektrum pada vowel statis justru membawa informasi vowel.

### 4.3 Sistem 1: DTW dengan averaged template

Pseudo code:

```
fungsi DTW(X, T):
    D[i][j] = jarak_euclid(X[i], T[j])
    C[0][0] = D[0][0]
    C[i][0] = C[i-1][0] + D[i][0];  C[0][j] = C[0][j-1] + D[0][j]
    C[i][j] = D[i][j] + min(C[i-1][j], C[i][j-1], C[i-1][j-1])
    path = backtrack dari (N-1, M-1)
    return C[N-1][M-1] / panjang(path)      # cost ternormalisasi

fungsi BuatTemplate(rekaman_vowel):
    ref = fitur rekaman pertama
    untuk tiap rekaman lain: align ke ref dengan DTW, kumpulkan frame
        yang terpetakan ke tiap frame ref
    template[k] = rata-rata semua frame yang terpetakan ke ref[k]

fungsi Kenali(audio):
    X = MFCC39(audio)
    untuk tiap vowel v: cost[v] = DTW(X, template[v])
    return argmin cost
```

Setiap vowel memiliki satu averaged template dari rekaman 1 tiap speaker kelompok (3 rekaman per vowel).

### 4.4 Sistem 2: Model Gaussian

Satu Gaussian multivariat 39 dimensi per vowel, dengan mean dan covariance penuh yang diestimasi dari seluruh frame rekaman latih vowel itu. Ridge 1e-3 ditambahkan ke diagonal covariance agar tetap dapat di-invers. Skor input adalah rata-rata negative log-likelihood per frame:

```
NLL(X | v) = rata-rata_t [ 0.5 * ( 39*log(2π) + log|Σ_v| + (x_t-μ_v)ᵀ Σ_v⁻¹ (x_t-μ_v) ) ]
prediksi = argmin_v NLL(X | v)
```

Model ini tidak memakai urutan waktu frame.

### 4.5 Skenario pengujian

| Skenario | Data uji | Jumlah |
|---|---|---|
| Closed Recording | rekaman 1 kelompok (sama dengan data latih) | 15 |
| Closed Speakers | rekaman 2 kelompok (speaker sama, rekaman berbeda) | 15 |
| Open Speakers | speaker kelompok lain (G04, G05, G07, G11) | 84 |
| Open (LOSO), tambahan | satu speaker kelompok ditahan, model dari 2 speaker lain, diuji pada kedua rekamannya | 30 |

Akurasi = prediksi benar / seluruh data uji × 100%. Rata-rata di Tabel 1 adalah rata-rata sederhana dari tiga skenario utama (tanpa LOSO).

### 4.6 Pengujian perangkat lunak

34 unit test (`test/test_pipeline.py`) untuk preprocessing, MFCC 39 dimensi, DTW (jarak, jalur monoton, template rata-rata), Gaussian (estimasi, rumus NLL, covariance definit positif), pengenalan pada sinyal sintetis, dan penghitungan akurasi. Semua lulus. Tes ini memeriksa kebenaran perhitungan, bukan akurasi pada rekaman asli.

## 5. Hasil Eksperimen

### Tabel 1. Akurasi (%)

| Sistem | Closed Recording | Closed Speakers | Open Speakers | Rata-rata |
|---|---|---|---|---|
| DTW Template | 100.0 | 86.7 | 70.2 | 85.6 |
| Model Gaussian | 100.0 | 93.3 | 58.3 | 83.9 |

Tambahan, open leave-one-speaker-out di dalam kelompok: DTW 66,7%, Gaussian 43,3%.

### Tabel 2. Akurasi per vowel (%)

| Sistem | Skenario | /a/ | /i/ | /u/ | /e/ | /o/ |
|---|---|---|---|---|---|---|
| DTW Template | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| DTW Template | Closed Speakers | 100.0 | 100.0 | 66.7 | 100.0 | 66.7 |
| DTW Template | Open Speakers | 100.0 | 82.4 | 58.8 | 43.8 | 64.7 |
| Model Gaussian | Closed Recording | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Closed Speakers | 66.7 | 100.0 | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Open Speakers | 52.9 | 100.0 | 35.3 | 31.2 | 70.6 |

### Tabel 3. Akurasi per speaker (%)

Closed (speaker kelompok):

| Sistem | Skenario | spk1 | spk2 | spk3 |
|---|---|---|---|---|
| DTW Template | Closed Recording | 100.0 | 100.0 | 100.0 |
| DTW Template | Closed Speakers | 100.0 | 100.0 | 60.0 |
| Model Gaussian | Closed Recording | 100.0 | 100.0 | 100.0 |
| Model Gaussian | Closed Speakers | 80.0 | 100.0 | 100.0 |

Open Speakers (tiap speaker 5 data uji, kecuali G05_S05 dengan 4):

| Speaker | DTW | Gaussian | Speaker | DTW | Gaussian |
|---|---|---|---|---|---|
| G04_S03 | 40.0 | 40.0 | G07_S03 | 100.0 | 100.0 |
| G04_S04 | 40.0 | 20.0 | G07_S04 | 100.0 | 100.0 |
| G05_S01 | 60.0 | 40.0 | G07_S05 | 40.0 | 40.0 |
| G05_S02 | 80.0 | 40.0 | G11_S01 | 40.0 | 60.0 |
| G05_S03 | 60.0 | 60.0 | G11_S02 | 100.0 | 100.0 |
| G05_S04 | 80.0 | 60.0 | G11_S03 | 100.0 | 80.0 |
| G05_S05 | 100.0 | 75.0 | G11_S04 | 80.0 | 60.0 |
| G07_S01 | 60.0 | 60.0 | G11_S05 | 100.0 | 40.0 |
| G07_S02 | 20.0 | 20.0 | | | |

### Confusion matrix, Open Speakers (baris = vowel benar, kolom = prediksi)

DTW Template:

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 17 | 0 | 0 | 0 | 0 |
| i | 0 | 14 | 1 | 0 | 2 |
| u | 0 | 1 | 10 | 0 | 6 |
| e | 2 | 4 | 2 | 7 | 1 |
| o | 4 | 1 | 1 | 0 | 11 |

Model Gaussian:

| benar \ prediksi | a | i | u | e | o |
|---|---|---|---|---|---|
| a | 9 | 6 | 0 | 0 | 2 |
| i | 0 | 17 | 0 | 0 | 0 |
| u | 0 | 5 | 6 | 0 | 6 |
| e | 0 | 10 | 1 | 5 | 0 |
| o | 4 | 1 | 0 | 0 | 12 |

Confusion matrix skenario lain dan seluruh prediksi ada di `results/results.md` dan `results/predictions.json`.

## 6. Analisis

Catatan: jumlah data uji kecil (15 pada skenario closed, 84 pada open), sehingga satu kesalahan menggeser akurasi closed sebesar 6,7 poin. Penjelasan penyebab di bawah adalah dugaan yang konsisten dengan hasil, belum diuji dengan eksperimen terkontrol.

### 6.1 Akurasi closed

Closed Recording menghasilkan 100% pada kedua sistem. Ini wajar: data uji identik dengan data pembentuk template dan model, sehingga angka ini tidak mengukur kemampuan generalisasi. Closed Speakers turun menjadi 86,7% (DTW) dan 93,3% (Gaussian). Perbedaannya satu data uji (13 vs 14 dari 15 benar), jadi tidak cukup untuk menyatakan Gaussian lebih baik pada closed speakers. Kesalahan DTW terjadi pada /u/ dan /o/ (tertukar), dua vowel belakang bulat yang secara akustik berdekatan.

### 6.2 Akurasi open

Pada Open Speakers DTW 70,2% dan Gaussian 58,3%, selisih 11,9 poin pada 84 data uji. Kedua sistem turun jauh dari closed, dan DTW lebih stabil. Rata-rata ketiga skenario: DTW 85,6%, Gaussian 83,9%, hampir sama karena keunggulan Gaussian di closed speakers diimbangi kelemahannya di open.

### 6.3 Mengapa DTW dan Gaussian berbeda

- **Informasi waktu.** DTW menyelaraskan urutan frame dan membandingkan terhadap template yang merupakan rata-rata beberapa rekaman. Gaussian mengumpulkan semua frame menjadi satu awan titik dan hanya menyimpan mean dan covariance, sehingga tidak ada informasi urutan.
- **Jumlah parameter vs data.** Covariance penuh 39×39 memiliki 780 parameter independen per vowel, sedangkan data latih hanya sekitar 3 rekaman (sekitar 300 frame yang berkorelasi kuat). Estimasi covariance karenanya rapuh dan perlu ridge. Model yang terlalu pas pada tiga speaker latih menghasilkan likelihood rendah untuk speaker baru. Ini sejalan dengan Gaussian yang kuat pada speaker yang dikenalnya (93,3% closed speakers) tetapi jatuh pada speaker baru.
- **Bias ke satu kelas.** Pada open, Gaussian memprediksi /i/ sebanyak 39 dari 84 kali (data /i/ hanya 17), dan /i/ benar 100%. Vowel lain sering "jatuh" ke /i/ (a: 6, u: 5, e: 10). Dugaan kami, covariance /i/ paling lebar sehingga likelihood-nya relatif tinggi untuk frame yang tidak cocok dengan model lain. Ini belum kami verifikasi (misalnya dengan membandingkan log-determinan covariance antar vowel).
- **Normalisasi cost DTW.** Cost dibagi panjang jalur sehingga durasi rekaman yang berbeda tidak langsung menaikkan cost.

### 6.4 Mengapa closed dan open berbeda

Pada closed, template dan model dibangun dari suara speaker yang sama dengan data uji, yaitu karakteristik yang sama pada saluran vokal (formant), kecepatan, mikrofon, dan kondisi rekaman. Pada open, speaker baru membawa formant, pitch, perangkat, dan lingkungan rekaman yang berbeda dari tiga speaker latih. Variasi antar speaker ini tidak terwakili dalam data latih. Kondisi kami lebih sulit karena hanya 3 speaker latih, dengan sample rate asal berbeda (satu 16 kHz, dua 48 kHz).

### 6.5 Pengaruh perbedaan speaker

Akurasi bergantung sangat besar pada speaker. Pada open, speaker yang dikenali sempurna oleh DTW mencapai 100% (G07_S03, G07_S04, G05_S05, G11_S02, G11_S03, G11_S05), sedangkan G07_S02 hanya 20% dan G04_S03, G04_S04, G07_S05, G11_S01 40%. Pada closed speakers, spk3 adalah yang tersulit untuk DTW (60%). Pada LOSO (dalam kelompok), speaker yang ditahan turun ke 60-80% (DTW) dan 20-70% (Gaussian). Penyebab per speaker (aksen, mikrofon, kecepatan bicara) tidak kami selidiki.

### 6.6 Pengaruh averaged template

Template dibangun dengan merata-ratakan frame dari 3 rekaman yang diselaraskan ke rekaman pertama. Rata-rata ini mengurangi kekhususan satu speaker dan, menurut dugaan kami, menjadi salah satu alasan DTW lebih tahan pada speaker baru dibanding Gaussian. Kami belum membandingkan dengan template tunggal atau template dengan rekaman referensi berbeda, sehingga kontribusi averaging belum terukur terpisah. Kelemahannya: hasil bergantung pada rekaman yang dipilih sebagai referensi, dan 3 rekaman masih sedikit.

### 6.7 Kesalahan pengenalan vowel

- **/a/** paling mudah untuk DTW (100% di semua skenario); untuk Gaussian 52,9% di open karena sering diprediksi /i/.
- **/e/** paling sulit di open (DTW 43,8%, Gaussian 31,2%). Pada DTW ia tersebar ke /i/ (4), /a/ (2), /u/ (2); pada Gaussian hampir seluruhnya ke /i/ (10 dari 16). Secara fonetik /e/ dan /i/ sama-sama vowel depan, sehingga kedekatan ini masuk akal, namun bagi DTW kesalahan /e/ juga ke vowel lain.
- **/u/ dan /o/** saling tertukar (DTW: u→o 6 kali, o→u 1 kali; Gaussian: u→o 6 kali). Keduanya vowel belakang bulat dengan formant rendah.
- **/i/** mudah untuk kedua sistem pada open (DTW 82,4%, Gaussian 100%), namun akurasi tinggi Gaussian ini sebagian disebabkan bias ke /i/ yang dijelaskan di 6.3.

## 7. Kesimpulan

1. Kedua sistem berhasil dibangun sesuai spesifikasi: MFCC 39 dimensi, DTW dengan averaged template, dan model Gaussian dengan mean serta covariance dengan negative log-likelihood.
2. Closed recording 100% pada kedua sistem (tidak menguji generalisasi). Pada closed speakers Gaussian 93,3% dan DTW 86,7%, selisih satu data uji.
3. Pada open speakers, DTW (70,2%) lebih baik dari Gaussian (58,3%). Rata-rata ketiga skenario DTW 85,6% dan Gaussian 83,9%.
4. Perbedaan speaker adalah faktor terbesar penurunan akurasi: akurasi per speaker open berkisar 20-100%.
5. Vowel tersulit pada open adalah /e/, dan pasangan /u/-/o/ paling sering tertukar. Gaussian cenderung bias ke /i/.
6. Keterbatasan: hanya 3 speaker latih (spesifikasi 5 speaker, 5 rekaman per template), data uji closed hanya 15, dan penyebab perbedaan kinerja belum diuji secara terkontrol.

## 8. Saran

- Tambah jumlah speaker dan rekaman latih (sesuai spesifikasi 5 speaker atau lebih) agar covariance Gaussian lebih stabil dan template lebih representatif.
- Gunakan covariance diagonal atau shrinkage, atau campuran Gaussian (GMM), dan bandingkan terhadap covariance penuh.
- Uji CMVN, pemilihan rekaman referensi template, dan metode averaging lain (misalnya DBA) untuk mengukur kontribusinya secara terpisah.
- Standarkan perangkat dan sample rate rekaman antar speaker.
- Laporkan akurasi dengan interval kepercayaan atau lakukan pengulangan dengan pembagian speaker berbeda, karena data uji kecil.

## 9. Pembagian Tugas

| Anggota | Tugas |
|---|---|
| `[ISI]` | `[ISI]` |
| `[ISI]` | `[ISI]` |
| `[ISI]` | `[ISI]` |

`[ISI: contoh pembagian: perekaman data, preprocessing/MFCC, DTW, Gaussian, evaluasi, laporan]`
