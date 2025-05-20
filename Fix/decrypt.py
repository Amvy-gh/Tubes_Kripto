from crypto_utils import load_private_key, decrypt_qr_data
from stegano_utils import extract_data_from_audio
import os

def main():
    try:
        print("=== DECRYPTION PROCESS ===")
        
        # 1. Get the stego audio file
        print("\n[1] Audio File Input")
        audio_path = input("Enter path to stego audio file: ")
        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file not found: {audio_path}")
            
        # 2. Get the private key
        print("\n[2] Private Key Input")
        key_path = input("Enter path to private key file (default: Keys/private_key.pem): ").strip()
        if not key_path:
            key_path = "Keys/private_key.pem"
        if not os.path.exists(key_path):
            raise ValueError(f"Private key file not found: {key_path}")

        # 3. Load private key
        print("\n[3] Loading Private Key...")
        private_key = load_private_key(key_path)
        print("[+] Private key loaded successfully")

        # 4. Extract data from audio
        print("\n[4] Extracting Hidden Data from Audio...")
        # We'll extract a large number of bits first
        initial_bits = 1000000  # We'll try with 1 million bits first
        extracted_data = extract_data_from_audio(audio_path, initial_bits)
        print("[+] Data extracted successfully")

        # 5. Reconstruct QR and decrypt
        print("\n[5] Reconstructing QR Code and Decrypting...")
        decrypted_text = decrypt_qr_data(private_key, extracted_data)
        
        if decrypted_text:
            print("\n=== DECRYPTION SUCCESSFUL! ✅ ===")
            print(f"Decrypted Message: {decrypted_text}")
        else:
            print("\n=== DECRYPTION FAILED! ❌ ===")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    main()