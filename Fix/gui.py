from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog,
                             QTabWidget, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from crypto_utils import generate_rsa_keys, display_keys, encrypt_data, create_qr_code, process_qr_image, load_private_key, decrypt_qr_data
from stegano_utils import embed_data_in_audio, extract_data_from_audio
import sys
import os

class SteganoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Steganography with RSA & QR")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Encryption tab
        encrypt_tab = QWidget()
        encrypt_layout = QVBoxLayout(encrypt_tab)

        encrypt_layout.addWidget(QLabel("Enter text to encrypt:"))
        self.text_input = QTextEdit()
        encrypt_layout.addWidget(self.text_input)

        encrypt_btn = QPushButton("Encrypt")
        encrypt_btn.clicked.connect(self.encrypt_text)
        encrypt_layout.addWidget(encrypt_btn)

        self.qr_label = QLabel()
        encrypt_layout.addWidget(self.qr_label)

        audio_layout = QHBoxLayout()
        self.audio_path_label = QLabel("No audio file selected")
        audio_btn = QPushButton("Select Audio File")
        audio_btn.clicked.connect(self.select_audio_file)
        audio_layout.addWidget(audio_btn)
        audio_layout.addWidget(self.audio_path_label)
        encrypt_layout.addLayout(audio_layout)

        embed_btn = QPushButton("Embed into Audio")
        embed_btn.clicked.connect(self.embed_qr_into_audio)
        encrypt_layout.addWidget(embed_btn)

        self.encrypt_progress = QProgressBar()
        encrypt_layout.addWidget(self.encrypt_progress)
        self.encrypt_status = QLabel("")
        encrypt_layout.addWidget(self.encrypt_status)

        # Decryption tab
        decrypt_tab = QWidget()
        decrypt_layout = QVBoxLayout(decrypt_tab)

        stego_layout = QHBoxLayout()
        self.stego_path_label = QLabel("No stego audio file selected")
        stego_btn = QPushButton("Select Stego Audio")
        stego_btn.clicked.connect(self.select_stego_file)
        stego_layout.addWidget(stego_btn)
        stego_layout.addWidget(self.stego_path_label)
        decrypt_layout.addLayout(stego_layout)

        key_layout = QHBoxLayout()
        self.key_path_label = QLabel("No private key selected")
        key_btn = QPushButton("Select Private Key")
        key_btn.clicked.connect(self.select_private_key)
        key_layout.addWidget(key_btn)
        key_layout.addWidget(self.key_path_label)
        decrypt_layout.addLayout(key_layout)

        decrypt_btn = QPushButton("Extract and Decrypt")
        decrypt_btn.clicked.connect(self.decrypt_process)
        decrypt_layout.addWidget(decrypt_btn)

        self.qr_label_decrypt = QLabel()
        decrypt_layout.addWidget(self.qr_label_decrypt)

        decrypt_layout.addWidget(QLabel("Decrypted Text:"))
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        decrypt_layout.addWidget(self.decrypted_text)

        self.decrypt_progress = QProgressBar()
        decrypt_layout.addWidget(self.decrypt_progress)
        self.decrypt_status = QLabel("")
        decrypt_layout.addWidget(self.decrypt_status)

        tabs.addTab(encrypt_tab, "Encrypt")
        tabs.addTab(decrypt_tab, "Decrypt")

        self.audio_path = None
        self.stego_path = None
        self.private_key_path = None
        self.encrypted_data = None
        self.compressed_data = None
        self.qr_path = None

    def select_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "WAV Files (*.wav)")
        if file_path:
            self.audio_path = file_path
            self.audio_path_label.setText(os.path.basename(file_path))

    def select_stego_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Stego Audio", "", "WAV Files (*.wav)")
        if file_path:
            self.stego_path = file_path
            self.stego_path_label.setText(os.path.basename(file_path))

    def select_private_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Private Key", "", "PEM Files (*.pem)")
        if file_path:
            self.private_key_path = file_path
            self.key_path_label.setText(os.path.basename(file_path))

    def encrypt_text(self):
        try:
            text = self.text_input.toPlainText()
            if not text:
                raise ValueError("Please enter text to encrypt!")

            self.encrypt_status.setText("Encrypting text and generating QR...")
            self.encrypt_progress.setValue(10)

            private_key, public_key = generate_rsa_keys()
            display_keys(private_key, public_key)

            self.encrypted_data = encrypt_data(public_key, text)
            self.qr_path = create_qr_code(self.encrypted_data)
            self.compressed_data = process_qr_image(self.qr_path)

            pixmap = QPixmap(self.qr_path)
            self.qr_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.encrypt_progress.setValue(50)
            self.encrypt_status.setText("QR Code generated. Ready to embed.")
        except Exception as e:
            self.encrypt_status.setText(f"Error: {str(e)}")

    def embed_qr_into_audio(self):
        try:
            if not self.audio_path or not self.compressed_data:
                raise ValueError("Please select audio file and encrypt text first.")

            self.encrypt_status.setText("Embedding QR into audio...")
            self.encrypt_progress.setValue(70)
            stego_file = embed_data_in_audio(self.audio_path, self.compressed_data)
            self.encrypt_progress.setValue(100)
            self.encrypt_status.setText(f"Stego audio saved as: {stego_file}")
        except Exception as e:
            self.encrypt_status.setText(f"Error: {str(e)}")

    def decrypt_process(self):
        try:
            if not self.stego_path or not self.private_key_path:
                raise ValueError("Please select stego audio and private key!")

            self.decrypt_status.setText("Decrypting...")
            self.decrypt_progress.setValue(20)

            private_key = load_private_key(self.private_key_path)
            extracted_data = extract_data_from_audio(self.stego_path, float('inf'))

            self.decrypt_progress.setValue(50)
            decrypted_text = decrypt_qr_data(private_key, extracted_data)

            # show QR
            with open("reconstructed_qr.png", "rb") as f:
                pixmap = QPixmap()
                pixmap.loadFromData(f.read())
                self.qr_label_decrypt.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))

            if not decrypted_text:
                raise ValueError("Decryption failed!")

            self.decrypted_text.setText(decrypted_text)
            self.decrypt_progress.setValue(100)
            self.decrypt_status.setText("Decryption successful!")

        except Exception as e:
            self.decrypt_status.setText(f"Error: {str(e)}")

        finally:
            self.decrypt_progress.setValue(0)

def main():
    app = QApplication(sys.argv)
    window = SteganoGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
