import os
from crypto_utils import generate_rsa_keys, encrypt_data, create_qr_code, process_qr_image, decrypt_qr_data
from stegano_utils import embed_data_in_audio, extract_data_from_audio
from evaluations import RSACryptoEvaluator, DWTSteganoEvaluator, run_evaluation
import tempfile

def main():
    print("=== STEGANOGRAFI AUDIO + RSA EVALUATION PIPELINE ===")

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

    # [8] Jalankan evaluasi lengkap
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

if __name__ == "__main__":
    main()
