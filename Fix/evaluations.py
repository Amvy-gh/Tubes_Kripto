import os
import numpy as np
import soundfile as sf
import time
import math
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
from skimage.metrics import structural_similarity as ssim
from crypto_utils import generate_rsa_keys, encrypt_data, create_qr_code, process_qr_image, decrypt_qr_data
from stegano_utils import embed_data_in_audio, extract_data_from_audio

# Class untuk evaluasi kriptografi RSA
class RSACryptoEvaluator:
    # Fungsi untuk menghitung waktu kunci dan enkripsi
    @staticmethod
    def compute_time(text):
        start_time = time.time()
        private_key, public_key = generate_rsa_keys()
        key_gen_time = time.time() - start_time

        start_time = time.time()
        encrypted = encrypt_data(public_key, text)
        encryption_time = time.time() - start_time

        return {
            "key_generation_time_sec": key_gen_time,
            "encryption_time_sec": encryption_time
        }
    
    # Fungsi untuk menghitung efek avalanche
    @staticmethod
    def avalanche_effect(text):
        private_key, public_key = generate_rsa_keys()
        encrypted1 = encrypt_data(public_key, text)
        # Modify one character (1 bit change)
        modified_text = text[:-1] + chr(ord(text[-1]) ^ 1)
        encrypted2 = encrypt_data(public_key, modified_text)

        diff_bits = sum(bin(a ^ b).count("1") for a, b in zip(encrypted1, encrypted2))
        total_bits = len(encrypted1) * 8

        return (diff_bits / total_bits) * 100  # percentage


# Class untuk evaluasi steganografi DWT
class DWTSteganoEvaluator:
    @staticmethod
    # Fungsi untuk mengevaluasi imperceptibility
    def evaluate_imperceptibility(original_audio_path, stego_audio_path):
        original, _ = sf.read(original_audio_path)
        stego, _ = sf.read(stego_audio_path)

        if original.ndim > 1:
            original = original.mean(axis=1)
        if stego.ndim > 1:
            stego = stego.mean(axis=1)

        mse = np.mean((original - stego) ** 2)
        max_val = np.max(np.abs(original))
        psnr = 100 if mse == 0 else 20 * math.log10(max_val / math.sqrt(mse))
        ssim_value = ssim(original, stego, data_range=original.max() - original.min())

        return {
            "psnr_dB": psnr,
            "ssim": ssim_value
        }

    @staticmethod
    # Fungsi untuk mengevaluasi kapasitas
    def evaluate_capacity(audio_path):
        audio, sr = sf.read(audio_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        total_samples = len(audio)
        capacity_bits = total_samples // 2
        capacity_bytes = capacity_bits // 8
        duration_sec = total_samples / sr
        bps = capacity_bits / duration_sec

        return {
            "capacity_bits": capacity_bits,
            "capacity_bytes": capacity_bytes,
            "duration_sec": duration_sec,
            "bits_per_second": bps
        }

    @staticmethod
    # Fungsi untuk mengevaluasi tingkat pemulihan
    def evaluate_recovery(original_text, stego_audio_path, private_key):
        try:
            extracted_data = extract_data_from_audio(stego_audio_path, float('inf'))
            decrypted_text = decrypt_qr_data(private_key, extracted_data)
            if decrypted_text == original_text:
                return {"success": True, "recovery_rate_percent": 100.0}
            else:
                match = sum(1 for a, b in zip(original_text, decrypted_text) if a == b)
                return {
                    "success": False,
                    "recovery_rate_percent": (match / len(original_text)) * 100
                }
        except Exception as e:
            return {"success": False, "recovery_rate_percent": 0.0, "error": str(e)}

# Fungsi untuk membuat perbandingan spektrogram
def create_spectrogram_comparison(original_audio_path, stego_audio_path, output_path="spectrogram_comparison.png"):
    """
    Buat perbandingan spektrogram antara audio original dan steganografi
    """
    print("📊 Membuat perbandingan spektrogram...")
    
    # Load audio files
    original, sr_orig = sf.read(original_audio_path)
    stego, sr_stego = sf.read(stego_audio_path)
    
    # Convert to mono jika stereo
    if original.ndim > 1:
        original = original.mean(axis=1)
    if stego.ndim > 1:
        stego = stego.mean(axis=1)
    
    # Pastikan panjang sama
    min_length = min(len(original), len(stego))
    original = original[:min_length]
    stego = stego[:min_length]
    
    # Generate spektrogram
    f_orig, t_orig, Sxx_orig = spectrogram(original, sr_orig, nperseg=1024, noverlap=512)
    f_stego, t_stego, Sxx_stego = spectrogram(stego, sr_stego, nperseg=1024, noverlap=512)
    
    # Convert ke dB scale
    Sxx_orig_db = 10 * np.log10(Sxx_orig + 1e-10)
    Sxx_stego_db = 10 * np.log10(Sxx_stego + 1e-10)
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Original spektrogram
    im1 = axes[0, 0].pcolormesh(t_orig, f_orig, Sxx_orig_db, shading='gouraud', cmap='viridis')
    axes[0, 0].set_title('Audio Original - Spektrogram')
    axes[0, 0].set_xlabel('Waktu (s)')
    axes[0, 0].set_ylabel('Frekuensi (Hz)')
    plt.colorbar(im1, ax=axes[0, 0], label='Power (dB)')
    
    # Stego spektrogram
    im2 = axes[0, 1].pcolormesh(t_stego, f_stego, Sxx_stego_db, shading='gouraud', cmap='viridis')
    axes[0, 1].set_title('Audio Steganografi - Spektrogram')
    axes[0, 1].set_xlabel('Waktu (s)')
    axes[0, 1].set_ylabel('Frekuensi (Hz)')
    plt.colorbar(im2, ax=axes[0, 1], label='Power (dB)')
    
    # Difference spektrogram
    diff_spectrum = Sxx_stego_db - Sxx_orig_db
    im3 = axes[1, 0].pcolormesh(t_orig, f_orig, diff_spectrum, shading='gouraud', cmap='RdBu_r')
    axes[1, 0].set_title('Perbedaan Spektrogram (Stego - Original)')
    axes[1, 0].set_xlabel('Waktu (s)')
    axes[1, 0].set_ylabel('Frekuensi (Hz)')
    plt.colorbar(im3, ax=axes[1, 0], label='Selisih Power (dB)')
    
    # Waveform comparison
    time_axis = np.linspace(0, len(original)/sr_orig, len(original))
    axes[1, 1].plot(time_axis[:5000], original[:5000], 'b-', label='Original', alpha=0.7)
    axes[1, 1].plot(time_axis[:5000], stego[:5000], 'r-', label='Steganografi', alpha=0.7)
    axes[1, 1].set_title('Perbandingan Waveform (5000 sampel pertama)')
    axes[1, 1].set_xlabel('Waktu (s)')
    axes[1, 1].set_ylabel('Amplitudo')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    print(f"   ✅ Spektrogram disimpan: {output_path}")
    plt.close()
    
    # Hitung statistik sederhana
    spectral_correlation = np.corrcoef(Sxx_orig.flatten(), Sxx_stego.flatten())[0, 1]
    max_diff = np.max(np.abs(diff_spectrum))
    mean_diff = np.mean(np.abs(diff_spectrum))
    
    return {
        "spectral_correlation": spectral_correlation,
        "max_difference_db": max_diff,
        "mean_difference_db": mean_diff,
        "plot_saved": output_path
    }

def run_evaluation(text_data, original_audio_path, stego_audio_path, private_key):
    print("\n=== [1] RSA CRYPTOGRAPHY EVALUATION ===")
    rsa_eval = RSACryptoEvaluator()
    timing = rsa_eval.compute_time(text_data)
    avalanche = rsa_eval.avalanche_effect(text_data)
    print(f"Key Generation Time: {timing['key_generation_time_sec']:.4f} sec")
    print(f"Encryption Time: {timing['encryption_time_sec']:.4f} sec")
    print(f"Avalanche Effect: {avalanche:.2f} %")

    print("\n=== [2] DWT STEGANOGRAPHY EVALUATION ===")
    steg_eval = DWTSteganoEvaluator()
    quality = steg_eval.evaluate_imperceptibility(original_audio_path, stego_audio_path)
    print(f"PSNR: {quality['psnr_dB']:.2f} dB")
    print(f"SSIM: {quality['ssim']:.4f}")

    capacity = steg_eval.evaluate_capacity(original_audio_path)
    print(f"Capacity: {capacity['capacity_bytes']} bytes ({capacity['bits_per_second']:.2f} bps)")

    recovery = steg_eval.evaluate_recovery(text_data, stego_audio_path, private_key)
    print(f"Recovery Rate: {recovery['recovery_rate_percent']:.2f} %")
    
    # === TAMBAHAN: SPEKTROGRAM ANALYSIS ===
    print("\n=== [3] SPEKTROGRAM ANALYSIS ===")
    spectral_analysis = create_spectrogram_comparison(original_audio_path, stego_audio_path)
    print(f"Spektral Correlation: {spectral_analysis['spectral_correlation']:.4f}")
    print(f"Max Difference: {spectral_analysis['max_difference_db']:.2f} dB")
    print(f"Mean Difference: {spectral_analysis['mean_difference_db']:.2f} dB")

    return {
        "rsa": {
            "timing": timing,
            "avalanche_effect_percent": avalanche
        },
        "steganography": {
            "imperceptibility": quality,
            "capacity": capacity,
            "recovery": recovery
        },
        "spectral_analysis": spectral_analysis
    }

def main():
    print("=== STEGANOGRAFI AUDIO + RSA EVALUATION dengan SPEKTROGRAM ===")

    # [1] Input Text
    text = input("Masukkan teks untuk dienkripsi: ").strip()

    # [2] Pilih file audio (cover)
    audio_path = input("Masukkan path ke file audio (WAV): ").strip()
    if not os.path.exists(audio_path):
        print("❌ File audio tidak ditemukan!")
        return

    # [3] Generate RSA Keys
    print("\n🔑 Membuat kunci RSA...")
    private_key, public_key = generate_rsa_keys()

    # [4] Enkripsi teks
    print("🔐 Mengenkripsi teks...")
    ciphertext = encrypt_data(public_key, text)

    # [5] Buat QR code dari hasil enkripsi
    print("📷 Membuat QR code...")
    qr_file = create_qr_code(ciphertext)

    # [6] Kompres gambar QR
    print("📦 Kompres QR code...")
    compressed_data = process_qr_image(qr_file)

    # [7] Sisipkan ke audio
    print("🎧 Menyisipkan ke audio...")
    stego_path = "stego_audio.wav"
    embed_data_in_audio(audio_path, compressed_data, output_path=stego_path)

    print(f"✅ Stego audio disimpan sebagai: {stego_path}")

    # [8] Jalankan evaluasi lengkap dengan spektrogram
    print("\n📊 Menjalankan evaluasi...")
    results = run_evaluation(text, audio_path, stego_path, private_key)

    print("\n=== HASIL EVALUASI ===")
    print_formatted_results(results)

def print_formatted_results(results):
    print("\n🛡️ [RSA]")
    t = results['rsa']['timing']
    print(f" - Key Generation: {t['key_generation_time_sec']:.4f} sec")
    print(f" - Encryption: {t['encryption_time_sec']:.4f} sec")
    print(f" - Avalanche Effect: {results['rsa']['avalanche_effect_percent']:.2f} %")

    print("\n🎧 [Steganografi Audio]")
    q = results['steganography']['imperceptibility']
    print(f" - PSNR: {q['psnr_dB']:.2f} dB")
    print(f" - SSIM: {q['ssim']:.4f}")

    c = results['steganography']['capacity']
    print(f" - Capacity: {c['capacity_bytes']} bytes ({c['bits_per_second']:.2f} bps)")

    r = results['steganography']['recovery']
    print(f" - Recovery Rate: {r['recovery_rate_percent']:.2f} %")
    if not r['success']:
        print(f" - Error: {r.get('error', 'Unknown Error')}")
    
    print("\n📊 [Spektrogram Analysis]")
    s = results['spectral_analysis']
    print(f" - Spektral Correlation: {s['spectral_correlation']:.4f}")
    print(f" - Max Difference: {s['max_difference_db']:.2f} dB")
    print(f" - Mean Difference: {s['mean_difference_db']:.2f} dB")
    print(f" - Plot File: {s['plot_saved']}")

if __name__ == "__main__":
    main()