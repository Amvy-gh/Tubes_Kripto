import numpy as np
import pywt
import soundfile as sf

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

def extract_data_from_audio(audio_path, expected_bit_length=float('inf')):
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

    # Konversi ke byte
    bit_string = ''.join(extracted_bits)
    byte_chunks = [bit_string[i:i+8] for i in range(0, len(bit_string), 8) if len(bit_string[i:i+8]) == 8]
    extracted_bytes = bytes([int(chunk, 2) for chunk in byte_chunks])
    print(f"[Extract] Data size: {len(extracted_bytes)} bytes")
    return extracted_bytes