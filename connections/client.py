import socket
import threading
import json
from files.error_handler import ErrorHandler
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from files.file_manager import FileManager


class ClientConnection:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_validator = False
        self.message_flags = None
        self.mac_address = None
        # Generowanie kluczy RSA
        self.private_key, self.public_key = self.generate_rsa_keys()

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connecting to [{self.host}:{self.port}]")
            self.connection_validator = True
            self.receive_message_flags()
            self.receive_messages()

        except Exception as e:
            ErrorHandler.error_handling("connect_to_server", e)
            self.client_socket.close()

    def generate_rsa_keys(self):
        rsa_key_pair = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = rsa_key_pair.public_key()
        FileManager.save_keys_to_files(rsa_key_pair)
        return rsa_key_pair, public_key

    def send_public_key(self):
        serialized_public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.client_socket.sendall(serialized_public_key + self.message_flags["END"])
        print("Public key sent to server.")

    def receive_public_key(self):
        server_public_key_pem = b""
        while True:
            chunk = self.client_socket.recv(1024)
            if not chunk:
                print("No more data received.")
                break
            if self.message_flags["END"] in chunk:
                server_public_key_pem += chunk.split(self.message_flags["END"])[0]
                print("End of public key marker received.")
                break
            server_public_key_pem += chunk

        server_public_key = serialization.load_pem_public_key(
            server_public_key_pem, backend=default_backend()
        )
        print("Server public key received.")
        return server_public_key

    def decrypt_with_private_key(self, encrypted_data):
        try:
            aes_key = self.private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return aes_key
        except Exception as e:
            ErrorHandler.error_handling("decrypt_with_private_key", e)
            return None

    def accept_file(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags["INFO"] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break

        except Exception as e:
            ErrorHandler.error_handling("accept_file", e)
            self.connection_validator = False

        print(
            f"Would you like to accept transfer of:\n {data.split(self.message_flags['INFO'])[0].decode()}"
        )
        choice = input("yes/no: ")
        try:
            if choice.lower() in ["yes", "y"]:
                self.client_socket.sendall(
                    self.message_flags["ACK"] + self.message_flags["INFO"]
                )
                return True
            else:
                self.client_socket.sendall(
                    self.message_flags["RST"] + self.message_flags["INFO"]
                )
                return False

        except Exception as e:
            ErrorHandler.error_handling("accept_file", e)
            return False

    def receive_file(self, chunk_size: int):
        try:
            EOF_flag = self.receive_EOF_flag()
            file_data = bytearray()
            chunk = b""

            while EOF_flag not in chunk:
                chunk = self.client_socket.recv(chunk_size)
                file_data += chunk
            return file_data

        except Exception as e:
            ErrorHandler.error_handling("receive_file", e)
            self.connection_validator = False

    def receive_EOF_flag(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags["INFO"] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break

        except Exception as e:
            ErrorHandler.error_handling("receive_EOF_flag", e)
            self.connection_validator = False
        return data.split(self.message_flags["INFO"])[0]

    def receive_message_flags(self):
        data = b""
        try:

            while self.connection_validator and b"/FLAGS/" not in data:
                data += self.client_socket.recv(1)

                if not data:
                    break
            message_flags_json = data.split(b"/FLAGS/")[0]
            self.message_flags = json.loads(message_flags_json.decode("utf-8"))
            self.message_flags = {
                key: value.encode("utf-8")
                for key, value in self.message_flags["flags"].items()
            }
            print(f"Received message flags from server: {self.message_flags}")

        except Exception as e:
            ErrorHandler.error_handling("receive_message_flags", e)
            self.connection_validator = False

    def receive_messages(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags["INFO"] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break

        except Exception as e:
            ErrorHandler.error_handling("receive_messages", e)
            self.connection_validator = False

        print(
            f"Received from server: [{data.split(self.message_flags['INFO'])[0].decode()}]"
        )
