from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path

encrypted_data = Path("sample_data.encrypted").read_bytes()

wrong_key = Fernet.generate_key()
cipher = Fernet(wrong_key)

try:
    cipher.decrypt(encrypted_data)
    print("Decryption successful")
except InvalidToken:
    print("Decryption failed: incorrect key")