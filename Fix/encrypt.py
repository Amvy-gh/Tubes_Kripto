from crypto_utils import generate_rsa_keys, display_keys, encrypt_data, create_qr_code, process_qr_image
from stegano_utils import embed_data_in_audio
import os

def main():
    try:
        print("=== ENCRYPTION STAGE ===")
        input_text = input("Enter text to encrypt: ")

        # 1. Generate RSA Key
        print("\n[1] Generating RSA Keys...")
        private_key, public_key = generate_rsa_keys()
        display_keys(private_key, public_key)

        # 2. Encrypt Text
        print("\n[2] Encrypting Text...")
        encrypted_data = encrypt_data(public_key, input_text)
        print(f"[+] Encrypted Size: {len(encrypted_data)} bytes")

        if len(encrypted_data) > 256:
            raise ValueError("Encrypted data exceeds RSA 2048-bit limit (256 bytes).")

        # 3. Generate QR Code
        print("\n[3] Generating QR Code...")
        qr_path = create_qr_code(encrypted_data)
        compressed_data = process_qr_image(qr_path)
        print(f"[+] QR Code generated and saved as '{qr_path}'")
        print(f"[+] Compressed QR size: {len(compressed_data)} bytes")

        # 4. Embed QR into Audio
        print("\n[4] Embedding Data in Audio...")
        audio_path = input("Enter path to WAV audio file: ")
        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")

        expected_bit_length = len(compressed_data) * 8
        stego_audio = embed_data_in_audio(audio_path, compressed_data)
        print(f"\n=== ENCRYPTION COMPLETE! ✅ ===")
        print(f"[+] Original text length: {len(input_text)} characters")
        print(f"[+] Final audio file: {stego_audio}")
        print("\nYou can now share the audio file. To decrypt, you will need:")
        print("1. The stego audio file")
        print("2. The private key (saved in Keys/private_key.pem)")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    main()