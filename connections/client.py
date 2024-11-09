import socket
import threading
import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
#from files.file_manager import FileManager

class ClientConnection:


    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_validator = False
        self.message_flags = None
        # Generowanie kluczy RSA
        self.private_key, self.public_key = self.generate_rsa_keys()




    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f'Connecting to {self.host}:{self.port}')
            self.connection_validator = True
            self.receive_message_flags()
            self.receive_messages()


            
        except ConnectionRefusedError:
            print(f'[ClientConnection.connect_to_server] Connection failed! The server is unavailable or refused the connection.')
            self.client_socket.close()
        except OSError as e:
            print(f'[ClientConnection.connect_to_server] OS error occurred: {e}')
            self.client_socket.close()
        except Exception as e:
            print(f'[ClientConnection.connect_to_server] An unexpected error occurred: {e}')
            self.client_socket.close()


    def generate_rsa_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        self.save_keys_to_files(private_key, public_key)
        return private_key, public_key


    def save_keys_to_files(self, private_key, public_key):
        with open('c_private_key.pem', 'wb') as private_key_file:
            private_key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open('c_public_key.pem', 'wb') as public_key_file:
            public_key_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("Private and public keys generated and saved.")


    def send_public_key(self):
        serialized_public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.client_socket.sendall(serialized_public_key + self.message_flags['END'])
        print("Public key sent to server.")


    def receive_public_key(self):
        server_public_key_pem = b""
        while True:
            chunk = self.client_socket.recv(1024)
            if not chunk:
                print("No more data received.")
                break
            if self.message_flags['END'] in chunk:
                server_public_key_pem += chunk.split(self.message_flags['END'])[0]
                print("End of public key marker received.")
                break
            server_public_key_pem += chunk

        server_public_key = serialization.load_pem_public_key(
            server_public_key_pem,
            backend=default_backend()
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
                    label=None
                )
            )
            return aes_key
        except Exception as e:
            print(f"An error occurred while decrypting: {e}")
            return None


    def accept_file(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags['INFO'] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break
        except ConnectionResetError:
            print(f'[ClientConnection.accept_file] Connection with the server was reset unexpectedly.')
            self.connection_validator = False
        except socket.timeout:
            print(f'[ClientConnection.accept_file] Timeout while waiting for data from server.')
            self.connection_validator = False
        except OSError as e:
            print(f'[ClientConnection.accept_file] OS error occurred during file acceptance: {e}')
            self.connection_validator = False
        except Exception as e:
            print(f'[ClientConnection.accept_file] An unexpected error occurred: {e}')
            self.connection_validator = False

        print(f'Would you like to accept transfer of:\n {data.split(self.message_flags['INFO'])[0].decode()}')
        choice = input('yes/no: ')
        try:
            if choice.lower() in ['yes', 'y']:
                self.client_socket.sendall(self.message_flags['ACK'] + self.message_flags['INFO'])
                return True
            else:
                self.client_socket.sendall(self.message_flags['RST'] + self.message_flags['INFO'])
                return False
        except BrokenPipeError:
            print(f'[ClientConnection.accept_file] Error: Tried to send data on a closed connection.')
            self.connection_validator = False
            return False
        except OSError as e:
            print(f'[ClientConnection.accept_file] OS error while sending response to server: {e}')
            return False
        except Exception as e:
            print(f'[ClientConnection.accept_file] An unexpected error occurred: {e}')
            return False


    def receive_file(self, chunk_size: int):
        try:
            EOF_flag = self.receive_EOF_flag()
            file_data = bytearray()
            chunk = b''

            while EOF_flag not in chunk:
                chunk = self.client_socket.recv(chunk_size)
                file_data += chunk
            return file_data
        except ConnectionResetError:
            print(f'[ClientConnection.receive_file] Connection with the server was reset during file reception.')
            self.connection_validator = False
        except OSError as e:
            print(f'[ClientConnection.receive_file] OS error occurred during file reception: {e}')
            self.connection_validator = False
        except Exception as e:
            print(f'[ClientConnection.receive_file] An unexpected error occurred during file reception: {e}')
            self.connection_validator = False


    def receive_EOF_flag(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags['INFO'] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break
        except ConnectionResetError:
            print(f'[ClientConnection.receive_messages] Connection with the server was reset unexpectedly.')
            self.connection_validator = False
        except socket.timeout:
            print(f'[ClientConnection.receive_messages] Timeout occurred while receiving data from the server.')
            self.connection_validator = False
        except OSError as e:
            print(f'[ClientConnection.receive_messages] OS error occurred while receiving data: {e}')
            self.connection_validator = False
        except Exception as e:
            print(f'[ClientConnection.receive_messages] An unexpected error occurred while receiving data: {e}')
            self.connection_validator = False
        return data.split(self.message_flags['INFO'])[0]


    def receive_message_flags(self):
        data = b""
        try:

            while self.connection_validator and b"/FLAGS/" not in data:
                data += self.client_socket.recv(1)

                if not data:
                    break
            message_flags_json = data.split(b"/FLAGS/")[0]
            self.message_flags = json.loads(message_flags_json.decode('utf-8'))
            self.message_flags = {
                key: value.encode('utf-8') 
                for key, value in self.message_flags['flags'].items()
                }
            print(f"Received message flags from server: {self.message_flags}")

        except ConnectionResetError:
            print(f'[ClientConnection.receive_messages] Connection with the server was reset unexpectedly.')
            self.connection_validator = False
        except socket.timeout:
            print(f'[ClientConnection.receive_messages] Timeout occurred while receiving data from the server.')
            self.connection_validator = False
        except OSError as e:
            print(f'[ClientConnection.receive_messages] OS error occurred while receiving data: {e}')
            self.connection_validator = False
        except Exception as e:
            print(f'[ClientConnection.receive_messages] An unexpected error occurred while receiving data: {e}')
            self.connection_validator = False


    def receive_messages(self):
        data = b""
        try:
            while self.connection_validator and self.message_flags['INFO'] not in data:
                data += self.client_socket.recv(1)
                if not data:
                    break

        except ConnectionResetError:
            print(f'[ClientConnection.receive_messages] Connection with the server was reset unexpectedly.')
            self.connection_validator = False
        except socket.timeout:
            print(f'[ClientConnection.receive_messages] Timeout occurred while receiving data from the server.')
            self.connection_validator = False
        except OSError as e:
            print(f'[ClientConnection.receive_messages] OS error occurred while receiving data: {e}')
            self.connection_validator = False
        except Exception as e:
            print(f'[ClientConnection.receive_messages] An unexpected error occurred while receiving data: {e}')
            self.connection_validator = False

        print(f'Received from server: {data.split(self.message_flags['INFO'])[0].decode()}')
