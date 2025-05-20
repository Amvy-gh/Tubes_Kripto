import numpy as np
import pywt
import soundfile as sf
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from PIL import Image
import qrcode
import zlib
import os

# 1. Generate RSA Keys
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# 2. Encrypt Data with RSA
def encrypt_data(public_key, data):
    ciphertext = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# 3. Create QR Code
def create_qr_code(data, filename='qr_code.png'):
    # Convert binary data to hex string for better QR encoding
    hex_data = data.hex()
    
    qr = qrcode.QRCode(
        version=40,  # Menggunakan versi maksimum
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Menggunakan error correction minimum untuk kapasitas maksimum
        box_size=10,
        border=4,
    )
    qr.add_data(hex_data)  # Menambahkan data dalam format hex
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# 4. Process QR Image (Binary + Compression)
def process_qr_image(image_path):
    img = Image.open(image_path).convert('1')  # Convert to binary (1-bit)
    width, height = img.size
    img_bytes = img.tobytes()
    
    # Add size info to header
    size_info = (width.to_bytes(2, 'big') + height.to_bytes(2, 'big'))
    compressed = zlib.compress(size_info + img_bytes)
    return compressed

# 5. Embed Data into Audio using DWT
def embed_data_in_audio(audio_path, data_bytes, output_path='stego_audio.wav'):
    print(f"[Embed] Data size: {len(data_bytes)} bytes")
    audio_data, sample_rate = sf.read(audio_path)
    
    # Konversi ke mono
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    # Konversi data ke bitstream
    data_bits = ''.join(format(byte, '08b') for byte in data_bytes)
    data_len = len(data_bits)
    print(f"[Embed] Total bit: {data_len}")

    # Alokasi ruang di audio
    if len(audio_data) * 8 < data_len:
        raise ValueError("Audio tidak cukup besar untuk menyimpan data.")

    # Gunakan DWT level 1
    coeffs = pywt.wavedec(audio_data, 'haar', level=1)
    approx, detail = coeffs

    # Sisipkan bit ke detail coefficients
    bit_index = 0
    detail_flat = np.copy(detail)
    scale_factor = 1000  # Untuk presisi float

    for i in range(len(detail_flat)):
        if bit_index >= data_len:
            break
        coeff_val = detail_flat[i] * scale_factor
        coeff_int = int(round(coeff_val))
        coeff_int = (coeff_int & ~1) | int(data_bits[bit_index])  # Ganti LSB
        detail_flat[i] = coeff_int / scale_factor
        bit_index += 1

    # Rekonstruksi audio
    coeffs_new = (approx, detail_flat)
    stego_audio = pywt.waverec(coeffs_new, 'haar')
    sf.write(output_path, stego_audio, sample_rate)
    print(f"[Embed] Data berhasil disisipkan: {bit_index} bit")
    return output_path

def extract_data_from_audio(audio_path, expected_bit_length):
    audio_data, sample_rate = sf.read(audio_path)
    
    # Konversi ke mono
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)
    
    # DWT
    coeffs = pywt.wavedec(audio_data, 'haar', level=1)
    approx, detail = coeffs

    # Ekstraksi bit
    extracted_bits = []
    scale_factor = 1000

    for coeff in detail:
        coeff_val = coeff * scale_factor
        coeff_int = int(round(coeff_val))
        extracted_bits.append(str(coeff_int & 1))
        if len(extracted_bits) >= expected_bit_length:
            break

    # Pastikan panjang bit sesuai
    if len(extracted_bits) < expected_bit_length:
        raise ValueError(f"Bit ekstraksi kurang: {len(extracted_bits)} dari {expected_bit_length}")

    # Konversi ke byte
    bit_string = ''.join(extracted_bits[:expected_bit_length])
    byte_chunks = [bit_string[i:i+8] for i in range(0, len(bit_string), 8) if len(bit_string[i:i+8]) == 8]
    extracted_bytes = bytes([int(chunk, 2) for chunk in byte_chunks])
    print(f"[Extract] Data size: {len(extracted_bytes)} bytes")
    return extracted_bytes

# 7. Reconstruct QR Image and Decrypt
def decrypt_qr_data(private_key, compressed_data):
    try:
        decompressed = zlib.decompress(compressed_data)
        width = int.from_bytes(decompressed[:2], 'big')
        height = int.from_bytes(decompressed[2:4], 'big')
        img_bytes = decompressed[4:]
        
        img = Image.frombytes('1', (width, height), img_bytes)
        img.save('reconstructed_qr.png')

        import cv2
        from pyzbar.pyzbar import decode

        img.save('temp_qr.png')
        cv_image = cv2.imread('temp_qr.png')
        codes = decode(cv_image)
        os.remove('temp_qr.png')

        if not codes:
            raise ValueError("QR Code tidak ditemukan dalam gambar.")        # Get hex string from QR and convert back to bytes
        hex_str = codes[0].data.decode('ascii')
        ciphertext = bytes.fromhex(hex_str)
        print(f"[Decrypt] Panjang ciphertext: {len(ciphertext)} bytes")

        if len(ciphertext) != 256:
            raise ValueError(f"Panjang ciphertext salah: {len(ciphertext)} byte, harus 256 byte")

        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext.decode()
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

# Main Program
def main():
    try:
        input_text = input("Enter text to encrypt: ")
        
        private_key, public_key = generate_rsa_keys()
        encrypted_data = encrypt_data(public_key, input_text)
        print(f"Encrypted Data: {encrypted_data} (Size: {len(encrypted_data)} bytes)")
        
        if len(encrypted_data) > 256:
            raise ValueError("Data enkripsi melebihi ukuran RSA 2048-bit (256 byte).")
        
        qr_path = create_qr_code(encrypted_data)
        compressed_data = process_qr_image(qr_path)
        print(f"Compressed Data Size: {len(compressed_data)} bytes")
        
        audio_path = input("Enter path to WAV audio file: ")
        expected_bit_length = len(compressed_data) * 8
        
        stego_audio = embed_data_in_audio(audio_path, compressed_data)
        print(f"Stego audio saved as: {stego_audio}")
        
        extracted_data = extract_data_from_audio(stego_audio, expected_bit_length)
        print(f"Extracted Data Size: {len(extracted_data)} bytes")
        
        decrypted_text = decrypt_qr_data(private_key, extracted_data)
        print(f"Decrypted Text: {decrypted_text}")
        print("Verification:", "Success!" if decrypted_text == input_text else "Failed!")
        
    except qrcode.exceptions.DataOverflowError as e:
        print(f"Error: QR code tidak dapat menampung data yang terlalu besar: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error tidak terduga: {e}")

if __name__ == "__main__":
    main()