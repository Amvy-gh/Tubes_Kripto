import numpy as np
import soundfile as sf
import time
import math
from scipy.signal import correlate
from skimage.metrics import structural_similarity as ssim
from crypto_utils import encrypt_data, decrypt_qr_data
from stegano_utils import extract_data_from_audio

class RSACryptoEvaluator:
    @staticmethod
    def compute_time(text):
        start_time = time.time()
        from crypto_utils import generate_rsa_keys
        private_key, public_key = generate_rsa_keys()
        key_gen_time = time.time() - start_time

        start_time = time.time()
        encrypted = encrypt_data(public_key, text)
        encryption_time = time.time() - start_time

        return {
            "key_generation_time_sec": key_gen_time,
            "encryption_time_sec": encryption_time
        }

    @staticmethod
    def avalanche_effect(text):
        from crypto_utils import generate_rsa_keys
        private_key, public_key = generate_rsa_keys()
        encrypted1 = encrypt_data(public_key, text)
        # Modify one character (1 bit change)
        modified_text = text[:-1] + chr(ord(text[-1]) ^ 1)
        encrypted2 = encrypt_data(public_key, modified_text)

        diff_bits = sum(bin(a ^ b).count("1") for a, b in zip(encrypted1, encrypted2))
        total_bits = len(encrypted1) * 8

        return (diff_bits / total_bits) * 100  # percentage

class DWTSteganoEvaluator:
    @staticmethod
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

    return {
        "rsa": {
            "timing": timing,
            "avalanche_effect_percent": avalanche
        },
        "steganography": {
            "imperceptibility": quality,
            "capacity": capacity,
            "recovery": recovery
        }
    }

if __name__ == "__main__":
    from crypto_utils import generate_rsa_keys
    text = "Hello from secure channel!"
    original_audio = "Audio/test-1.wav"
    stego_audio = "stego_audio.wav"
    private_key, _ = generate_rsa_keys()
    results = run_evaluation(text, original_audio, stego_audio, private_key)
    print("\nFinal Results:\n", results)
