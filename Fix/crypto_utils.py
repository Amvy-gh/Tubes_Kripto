from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from PIL import Image
import qrcode
import zlib
import os
import cv2
from pyzbar.pyzbar import decode

def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def display_keys(private_key, public_key, save_to_file=True):
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    print("\n===== PUBLIC KEY =====")
    print(public_pem.decode())
    print("===== PRIVATE KEY =====")
    print(private_pem.decode())

    if save_to_file:
        # Save to Keys directory
        os.makedirs("Keys", exist_ok=True)
        with open("Keys/public_key.pem", "wb") as f:
            f.write(public_pem)
        with open("Keys/private_key.pem", "wb") as f:
            f.write(private_pem)
        print("\nKeys saved in 'Keys' directory")

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

def create_qr_code(data, filename='qr_code.png'):
    hex_data = data.hex()
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(hex_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

def process_qr_image(image_path):
    img = Image.open(image_path).convert('1')
    width, height = img.size
    img_bytes = img.tobytes()
    
    size_info = (width.to_bytes(2, 'big') + height.to_bytes(2, 'big'))
    compressed = zlib.compress(size_info + img_bytes)
    return compressed

def decrypt_qr_data(private_key, compressed_data):
    try:
        decompressed = zlib.decompress(compressed_data)
        width = int.from_bytes(decompressed[:2], 'big')
        height = int.from_bytes(decompressed[2:4], 'big')
        img_bytes = decompressed[4:]
        
        img = Image.frombytes('1', (width, height), img_bytes)
        img.save('reconstructed_qr.png')
        print("[+] QR Code reconstructed and saved as 'reconstructed_qr.png'")

        img.save('temp_qr.png')
        cv_image = cv2.imread('temp_qr.png')
        codes = decode(cv_image)
        os.remove('temp_qr.png')

        if not codes:
            raise ValueError("QR Code tidak ditemukan dalam gambar.")
        
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

def load_private_key(key_path):
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key