# 🎧 Audio Steganografi + RSA Encryption

Proyek ini merupakan implementasi steganografi audio menggunakan *DWT (Discrete Wavelet Transform)* dan *RSA cryptography*.
Teks akan dienkripsi menggunakan RSA, diubah menjadi QR code, lalu disisipkan ke dalam file audio `.wav`.
Proses ini mendukung enkripsi, penyisipan ke audio, dekripsi kembali, serta evaluasi kualitas dan keamanan.

---

## 📁 Struktur Folder

* `gui.py` — Antarmuka pengguna berbasis PyQt5 untuk proses enkripsi dan dekripsi.
* `evaluations-run.py` — Jalur cepat untuk menjalankan seluruh pipeline dan evaluasi langsung dari terminal.
* `create.wav` — Script pembuat file audio dummy untuk pengujian awal.
* `fix/` — Folder keluaran dari `create.wav`, digunakan sebagai input untuk GUI.

---

## 📦 Instalasi Dependensi

Pastikan kamu sudah menginstal semua library yang dibutuhkan dengan perintah berikut:

```bash
pip install pyqt5 cryptography numpy soundfile pywavelets pillow qrcode opencv-python pyzbar scikit-image
```

---

## 🔁 Alur Penggunaan

Berikut adalah langkah-langkah untuk menggunakan aplikasi ini secara menyeluruh:

### 1. Masuk ke Direktori Proyek

Pindah ke folder utama proyek:

```bash
cd Utils
```

### 2. Jalankan Script Generator Audio Dummy

Script ini akan membuat file audio dasar untuk keperluan penyisipan data.

```bash
python create.wav
```

Setelah dijalankan, akan muncul folder `fix/` yang berisi file audio `.wav`.

### 3. Jalankan GUI (Antarmuka Pengguna)

Masuk ke folder `fix` dan jalankan GUI:

```bash
cd fix
python ../gui.py
```

### 4. Proses Enkripsi melalui GUI

* Masukkan teks pada tab **Encrypt**.
* Klik tombol **Encrypt** → QR code dan ciphertext akan muncul.
* Pilih file audio hasil dari `create.wav`.
* Klik tombol **Embed into Audio** → Akan dihasilkan file `stego_audio.wav`.

### 5. Proses Dekripsi melalui GUI

Masuk ke tab **Decrypt**:

* Pilih file `stego_audio.wav`.
* Pilih file `private_key.pem` (yang otomatis dihasilkan saat enkripsi).
* Klik tombol **Extract and Decrypt**.
* Jika berhasil, QR code dan teks asli akan muncul di layar.

### 6. Evaluasi Kualitas & Keamanan

Setelah semua proses selesai, kamu bisa mengevaluasi kualitas steganografi dan enkripsi.

Kembali ke direktori utama:

```bash
cd ..
python evaluations-run.py
```

Lalu masukkan:

* Teks asli yang ingin dienkripsi.
* Path ke audio hasil penyisipan (`fix/stego_audio.wav`).

Hasil evaluasi akan mencakup:

* Waktu enkripsi dan pembuatan kunci RSA.
* Avalanche effect dari RSA.
* Nilai PSNR & SSIM dari hasil steganografi.
* Kapasitas penyisipan data.
* Tingkat keberhasilan dekripsi pesan.

---

## 📊 Evaluasi

* 🔐 **RSA**:

  * Waktu enkripsi dan dekripsi
  * Avalanche effect (perubahan besar akibat 1 bit berbeda)

* 🎧 **Steganografi Audio**:

  * PSNR (Peak Signal-to-Noise Ratio)
  * SSIM (Structural Similarity Index)
  * Kapasitas penyisipan (bit/detik)
  * Tingkat keberhasilan pemulihan pesan

---
