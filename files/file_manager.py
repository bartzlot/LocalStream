import os
import pathlib
import json
from files.error_handler import ErrorHandler
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class FileManager:


    @staticmethod
    def read_json(file_path: str):

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data

        except Exception as e:
            ErrorHandler.error_handling("read_json", e)

        return None

    @staticmethod
    def encrypt_file(file_path, key):
        iv = os.urandom(16)  # 16 bytes IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        try:
            with open(file_path, 'rb') as f:
                plaintext = f.read()

            # Padding (PKCS7) for AES block size of 16 bytes
            padding_length = 16 - len(plaintext) % 16
            plaintext += bytes([padding_length]) * padding_length

            ciphertext = encryptor.update(plaintext) + encryptor.finalize()

            encrypted_file_path = file_path + '.enc'
            with open(encrypted_file_path, 'wb') as f:
                f.write(iv + ciphertext)  # Save IV + ciphertext

            print(f"File encrypted: {encrypted_file_path}")
            return encrypted_file_path

        except Exception as e:
            ErrorHandler.error_handling("encrypt_file", e)

        return None

    @staticmethod
    def decrypt_file(encrypted_file_path, key):
        try:
            with open(encrypted_file_path, 'rb') as f:
                iv = f.read(16)  # First 16 bytes for IV
                ciphertext = f.read()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

            # Usunięcie paddingu
            padding_length = plaintext_padded[-1]
            plaintext = plaintext_padded[:-padding_length]

            decrypted_file_path = encrypted_file_path.replace('.enc', '')
            with open(decrypted_file_path, 'wb') as f:
                f.write(plaintext)

            print(f"File decrypted: {decrypted_file_path}")
            return decrypted_file_path

        except Exception as e:
            ErrorHandler.error_handling("decrypt_file", e)

        return None

    @staticmethod
    def read_file(file_path: str, chunk_size: int, EOF_flag: bytes):

        try:
            with open(file_path, 'rb') as file:
                print(f"File '{file_path}' successfully loaded.")
                file_data = b""

                while True:
                    chunk = file.read(chunk_size)

                    if not chunk:
                        file_data += EOF_flag
                        break

                    file_data += chunk

                file_name = os.path.basename(file_path)
                
                file_size_bytes = os.path.getsize(file_path)
            
                if file_size_bytes < 1024:  
                    file_size = f"{file_size_bytes} B"
                elif file_size_bytes < 1024**2:
                    file_size = f"{file_size_bytes / 1024:.2f} KB"
                else:  
                    file_size = f"{round(file_size_bytes / 1024**2, 2)} MB"
                    
                file_ext = pathlib.Path(file_path).suffix

                return [file_data, file_name, file_size, file_ext]

        except Exception as e:
            ErrorHandler.error_handling("read_file", e)

        return None

    @staticmethod
    def save_file(file_path: str, file_bytes: bytes, EOF_flag: bytes):

        try:
            with open(file_path, "wb") as file:
                file.write(file_bytes.split(EOF_flag)[0])

        except Exception as e:
            ErrorHandler.error_handling("save_file", e)

        return None

    @staticmethod
    def delete_file(file_path):
        try:
            os.remove(file_path)
            print(f"File '{file_path}' successfully deleted.")

        except Exception as e:
            ErrorHandler.error_handling("delete_file", e)



