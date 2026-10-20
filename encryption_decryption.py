from cryptography.fernet import Fernet
from pathlib import Path

input_file = Path("sample_data.csv")
encrypted_file = Path("sample_data.encrypted")
decrypted_file = Path("decrypted_data.csv")
key_file = Path("encryption.key")

key = Fernet.generate_key()
key_file.write_bytes(key)

cipher = Fernet(key)

original_data = input_file.read_bytes()

encrypted_data = cipher.encrypt(original_data)
encrypted_file.write_bytes(encrypted_data)

print("CSV file encrypted successfully.")
print("Encrypted file:", encrypted_file)

loaded_key = key_file.read_bytes()
decryptor = Fernet(loaded_key)

decrypted_data = decryptor.decrypt(
    encrypted_file.read_bytes()
)

decrypted_file.write_bytes(decrypted_data)

print("CSV file decrypted successfully.")
print("Decrypted file:", decrypted_file)

if input_file.read_bytes() == decrypted_file.read_bytes():
    print("Verification successful: files match.")
else:
    print("Verification failed: files differ.")
