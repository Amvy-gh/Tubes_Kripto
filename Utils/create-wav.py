import numpy as np
import soundfile as sf
import argparse

def generate_silence_wav(duration=5, sample_rate=44100, output="silence.wav"):
    """
    Generate file WAV kosong (silence) dengan durasi tertentu.
    
    Args:
        duration (int): Durasi file audio dalam detik.
        sample_rate (int): Sample rate audio (default: 44100 Hz).
        output (str): Nama file output WAV.
    """
    # Buat data audio kosong (mono)
    silence = np.zeros(int(sample_rate * duration), dtype=np.float32)
    
    # Simpan ke file WAV
    sf.write(output, silence, sample_rate)
    print(f"File WAV kosong berhasil dibuat: {output}")
    print(f"Durasi: {duration} detik, Sample Rate: {sample_rate} Hz")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate file WAV kosong untuk steganografi.")
    parser.add_argument("--duration", type=int, default=5, help="Durasi file audio dalam detik (default: 5)")
    parser.add_argument("--samplerate", type=int, default=44100, help="Sample rate audio (default: 44100 Hz)")
    parser.add_argument("--output", type=str, default="silence.wav", help="Nama file output WAV (default: silence.wav)")
    
    args = parser.parse_args()
    generate_silence_wav(args.duration, args.samplerate, args.output)