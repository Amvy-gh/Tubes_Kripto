# Audio Steganografi + RSA Encryption

Proyek ini adalah implementasi sederhana dari steganografi audio menggunakan transformasi DWT dan kriptografi RSA.  
Teks yang dienkripsi akan disisipkan dalam file audio dan dapat diekstrak serta dievaluasi kembali.

## 📁 Struktur Utama

- `gui.py` — Antarmuka GUI untuk enkripsi & dekripsi menggunakan PyQt5.
- `evaluations-run.py` — Jalur cepat untuk menjalankan pipeline enkripsi ➝ steganografi ➝ evaluasi langsung dari terminal.

## 📦 Library yang Dibutuhkan

Install semua dependensi menggunakan:

```bash
pip install pyqt5 cryptography numpy soundfile pywavelets pillow qrcode opencv-python pyzbar scikit-image
