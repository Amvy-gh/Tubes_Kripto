from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog,
                             QTabWidget, QProgressBar, QMessageBox, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from crypto_utils import generate_rsa_keys, display_keys, encrypt_data, create_qr_code, process_qr_image, load_private_key, decrypt_qr_data
from stegano_utils import embed_data_in_audio, extract_data_from_audio
import sys
import os
import base64

# Class untuk GUI Steganografi Audio
class SteganoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Steganography with RSA & QR")
        self.setGeometry(100, 100, 800, 650)  # Made window slightly taller
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
            }
            QTabWidget::pane { 
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e6e6e6;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
            QProgressBar {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                background-color: #f0f0f0;
                height: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
                border-radius: 3px;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title label
        title_label = QLabel("Audio Steganography with RSA & QR")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Encryption tab
        encrypt_tab = QWidget()
        encrypt_layout = QVBoxLayout(encrypt_tab)
        encrypt_layout.setContentsMargins(15, 15, 15, 15)
        encrypt_layout.setSpacing(12)

        # Text input section
        input_label = QLabel("Enter text to encrypt:")
        input_label.setAlignment(Qt.AlignLeft)
        encrypt_layout.addWidget(input_label)
        
        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(80)  # Decreased slightly to make room
        encrypt_layout.addWidget(self.text_input)

        # Encrypt button with spacers for centering
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        encrypt_btn = QPushButton("Encrypt")
        encrypt_btn.setMinimumWidth(150)
        encrypt_btn.clicked.connect(self.encrypt_text)
        button_layout.addWidget(encrypt_btn)
        button_layout.addStretch(1)
        encrypt_layout.addLayout(button_layout)

        # Ciphertext display area (new addition with separate columns)
        cipher_section = QVBoxLayout()
        cipher_section.setSpacing(10)
        
        ciphertext_label = QLabel("Encrypted Ciphertext:")
        ciphertext_label.setAlignment(Qt.AlignLeft)
        cipher_section.addWidget(ciphertext_label)
        
        # Create layout for the two formats side by side
        cipher_formats_layout = QHBoxLayout()
        
        # HEX format column
        hex_layout = QVBoxLayout()
        hex_label = QLabel("HEX Format:")
        hex_label.setStyleSheet("font-weight: bold;")
        hex_layout.addWidget(hex_label)
        
        self.hex_display = QTextEdit()
        self.hex_display.setReadOnly(True)
        self.hex_display.setMinimumHeight(70)
        hex_layout.addWidget(self.hex_display)
        cipher_formats_layout.addLayout(hex_layout)
        
        # BASE64 format column
        base64_layout = QVBoxLayout()
        base64_label = QLabel("BASE64 Format:")
        base64_label.setStyleSheet("font-weight: bold;")
        base64_layout.addWidget(base64_label)
        
        self.base64_display = QTextEdit()
        self.base64_display.setReadOnly(True)
        self.base64_display.setMinimumHeight(70)
        base64_layout.addWidget(self.base64_display)
        cipher_formats_layout.addLayout(base64_layout)
        
        cipher_section.addLayout(cipher_formats_layout)
        encrypt_layout.addLayout(cipher_section)

        # QR code display area with frame
        qr_layout = QHBoxLayout()
        qr_layout.addStretch(1)
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setStyleSheet("border: 1px solid #dcdcdc; background-color: white;")
        self.qr_label.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(self.qr_label)
        qr_layout.addStretch(1)
        encrypt_layout.addLayout(qr_layout)

        # File selection section
        file_section = QVBoxLayout()
        file_section.setSpacing(10)
        
        # Audio file selection
        audio_layout = QHBoxLayout()
        audio_label = QLabel("Audio File:")
        audio_label.setFixedWidth(80)
        audio_layout.addWidget(audio_label)
        
        self.audio_path_label = QLabel("No audio file selected")
        self.audio_path_label.setStyleSheet("color: #666666;")
        audio_layout.addWidget(self.audio_path_label, 1)
        
        audio_btn = QPushButton("Browse...")
        audio_btn.setFixedWidth(100)
        audio_btn.clicked.connect(self.select_audio_file)
        audio_layout.addWidget(audio_btn)
        file_section.addLayout(audio_layout)
        
        # Embed button
        embed_layout = QHBoxLayout()
        embed_layout.addStretch(1)
        embed_btn = QPushButton("Embed into Audio")
        embed_btn.setMinimumWidth(200)
        embed_btn.clicked.connect(self.embed_qr_into_audio)
        embed_layout.addWidget(embed_btn)
        embed_layout.addStretch(1)
        file_section.addLayout(embed_layout)
        
        encrypt_layout.addLayout(file_section)

        # Progress and status
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        
        self.encrypt_progress = QProgressBar()
        progress_layout.addWidget(self.encrypt_progress)
        
        self.encrypt_status = QLabel("")
        self.encrypt_status.setStyleSheet("color: #4a86e8; font-weight: bold;")
        self.encrypt_status.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.encrypt_status)
        
        encrypt_layout.addLayout(progress_layout)
        encrypt_layout.addStretch(1)

        # Decryption tab
        decrypt_tab = QWidget()
        decrypt_layout = QVBoxLayout(decrypt_tab)
        decrypt_layout.setContentsMargins(15, 15, 15, 15)
        decrypt_layout.setSpacing(12)

        # File selection for decryption
        decrypt_file_section = QVBoxLayout()
        decrypt_file_section.setSpacing(10)
        
        # Stego audio file selection
        stego_layout = QHBoxLayout()
        stego_label = QLabel("Stego Audio:")
        stego_label.setFixedWidth(80)
        stego_layout.addWidget(stego_label)
        
        self.stego_path_label = QLabel("No stego audio file selected")
        self.stego_path_label.setStyleSheet("color: #666666;")
        stego_layout.addWidget(self.stego_path_label, 1)
        
        stego_btn = QPushButton("Browse...")
        stego_btn.setFixedWidth(100)
        stego_btn.clicked.connect(self.select_stego_file)
        stego_layout.addWidget(stego_btn)
        decrypt_file_section.addLayout(stego_layout)
        
        # Private key selection
        key_layout = QHBoxLayout()
        key_label = QLabel("Private Key:")
        key_label.setFixedWidth(80)
        key_layout.addWidget(key_label)
        
        self.key_path_label = QLabel("No private key selected")
        self.key_path_label.setStyleSheet("color: #666666;")
        key_layout.addWidget(self.key_path_label, 1)
        
        key_btn = QPushButton("Browse...")
        key_btn.setFixedWidth(100)
        key_btn.clicked.connect(self.select_private_key)
        key_layout.addWidget(key_btn)
        decrypt_file_section.addLayout(key_layout)
        
        decrypt_layout.addLayout(decrypt_file_section)

        # Decrypt button
        decrypt_btn_layout = QHBoxLayout()
        decrypt_btn_layout.addStretch(1)
        decrypt_btn = QPushButton("Extract and Decrypt")
        decrypt_btn.setMinimumWidth(200)
        decrypt_btn.clicked.connect(self.decrypt_process)
        decrypt_btn_layout.addWidget(decrypt_btn)
        decrypt_btn_layout.addStretch(1)
        decrypt_layout.addLayout(decrypt_btn_layout)

        # Extracted ciphertext display (with separate columns)
        extracted_section = QVBoxLayout()
        extracted_section.setSpacing(10)
        
        decrypt_cipher_label = QLabel("Extracted Ciphertext:")
        extracted_section.addWidget(decrypt_cipher_label)
        
        # Create layout for the two formats side by side
        extracted_formats_layout = QHBoxLayout()
        
        # HEX format column
        extracted_hex_layout = QVBoxLayout()
        extracted_hex_label = QLabel("HEX Format:")
        extracted_hex_label.setStyleSheet("font-weight: bold;")
        extracted_hex_layout.addWidget(extracted_hex_label)
        
        self.extracted_hex_display = QTextEdit()
        self.extracted_hex_display.setReadOnly(True)
        self.extracted_hex_display.setMinimumHeight(70)
        extracted_hex_layout.addWidget(self.extracted_hex_display)
        extracted_formats_layout.addLayout(extracted_hex_layout)
        
        # BASE64 format column
        extracted_base64_layout = QVBoxLayout()
        extracted_base64_label = QLabel("BASE64 Format:")
        extracted_base64_label.setStyleSheet("font-weight: bold;")
        extracted_base64_layout.addWidget(extracted_base64_label)
        
        self.extracted_base64_display = QTextEdit()
        self.extracted_base64_display.setReadOnly(True)
        self.extracted_base64_display.setMinimumHeight(70)
        extracted_base64_layout.addWidget(self.extracted_base64_display)
        extracted_formats_layout.addLayout(extracted_base64_layout)
        
        extracted_section.addLayout(extracted_formats_layout)
        decrypt_layout.addLayout(extracted_section)

        # QR Display for decryption
        decrypt_qr_layout = QHBoxLayout()
        decrypt_qr_layout.addStretch(1)
        self.qr_label_decrypt = QLabel()
        self.qr_label_decrypt.setFixedSize(200, 200)
        self.qr_label_decrypt.setStyleSheet("border: 1px solid #dcdcdc; background-color: white;")
        self.qr_label_decrypt.setAlignment(Qt.AlignCenter)
        decrypt_qr_layout.addWidget(self.qr_label_decrypt)
        decrypt_qr_layout.addStretch(1)
        decrypt_layout.addLayout(decrypt_qr_layout)

        # Decrypted text
        decrypt_layout.addWidget(QLabel("Decrypted Text:"))
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        self.decrypted_text.setMinimumHeight(80)
        decrypt_layout.addWidget(self.decrypted_text)

        # Progress and status for decryption
        decrypt_progress_layout = QVBoxLayout()
        decrypt_progress_layout.setSpacing(5)
        
        self.decrypt_progress = QProgressBar()
        decrypt_progress_layout.addWidget(self.decrypt_progress)
        
        self.decrypt_status = QLabel("")
        self.decrypt_status.setStyleSheet("color: #4a86e8; font-weight: bold;")
        self.decrypt_status.setAlignment(Qt.AlignCenter)
        decrypt_progress_layout.addWidget(self.decrypt_status)
        
        decrypt_layout.addLayout(decrypt_progress_layout)
        decrypt_layout.addStretch(1)

        # Add tabs to tab widget
        tabs.addTab(encrypt_tab, "Encrypt")
        tabs.addTab(decrypt_tab, "Decrypt")

        # Instance variables
        self.audio_path = None
        self.stego_path = None
        self.private_key_path = None
        self.encrypted_data = None
        self.compressed_data = None
        self.qr_path = None
        
        # Set window height to accommodate the new elements
        self.setGeometry(100, 100, 800, 700)  # Increased height from 650 to 700
        
        
    #  fungsi untuk memilih file audio
    def select_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "WAV Files (*.wav)")
        if file_path:
            self.audio_path = file_path
            self.audio_path_label.setText(os.path.basename(file_path))
     
    # fungsi untuk memilih file stego
    def select_stego_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Stego Audio", "", "WAV Files (*.wav)")
        if file_path:
            self.stego_path = file_path
            self.stego_path_label.setText(os.path.basename(file_path))

    # fungsi untuk memilih file kunci privat
    def select_private_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Private Key", "", "PEM Files (*.pem)")
        if file_path:
            self.private_key_path = file_path
            self.key_path_label.setText(os.path.basename(file_path))
            
            
    # fungsi untuk mengenkripsi teks
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
            
            # Display ciphertext in both formats
            ciphertext_hex = self.encrypted_data.hex()
            ciphertext_b64 = base64.b64encode(self.encrypted_data).decode('utf-8')
            
            # Truncate hex if too long, with ellipsis in the middle
            if len(ciphertext_hex) > 100:
                hex_display = ciphertext_hex[:45] + "..." + ciphertext_hex[-45:]
            else:
                hex_display = ciphertext_hex
                
            # Update separate displays
            self.hex_display.setText(hex_display)
            self.base64_display.setText(ciphertext_b64)
            
            self.encrypt_progress.setValue(30)
            
            self.qr_path = create_qr_code(self.encrypted_data)
            self.compressed_data = process_qr_image(self.qr_path)

            pixmap = QPixmap(self.qr_path)
            self.qr_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.encrypt_progress.setValue(50)
            self.encrypt_status.setText("QR Code generated. Ready to embed.")
        except Exception as e:
            self.encrypt_status.setText(f"Error: {str(e)}")

    
    # fungsi untuk menyisipkan QR ke dalam audio
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


    # fungsi untuk mendekripsi data
    def decrypt_process(self):
        try:
            if not self.stego_path or not self.private_key_path:
                raise ValueError("Please select stego audio and private key!")

            self.decrypt_status.setText("Extracting data from audio...")
            self.decrypt_progress.setValue(20)

            private_key = load_private_key(self.private_key_path)
            extracted_data = extract_data_from_audio(self.stego_path, float('inf'))
            
            # Display the extracted ciphertext in both formats
            extracted_hex = extracted_data.hex()
            extracted_b64 = base64.b64encode(extracted_data).decode('utf-8')
            
            # Truncate hex if too long, with ellipsis in the middle
            if len(extracted_hex) > 100:
                hex_display = extracted_hex[:45] + "..." + extracted_hex[-45:]
            else:
                hex_display = extracted_hex
                
            # Update separate displays
            self.extracted_hex_display.setText(hex_display)
            self.extracted_base64_display.setText(extracted_b64)
            
            self.decrypt_progress.setValue(50)
            self.decrypt_status.setText("Decrypting extracted data...")
            
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
            self.decrypt_progress.setValue(0)  # Only reset progress bar on error

# fungsi utama untuk menjalankan aplikasi
def main():
    app = QApplication(sys.argv)
    window = SteganoGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()