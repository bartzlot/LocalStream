import socket
import threading
import json
from os.path import join, dirname, abspath
from files.file_manager import FileManager
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class ServerConnection:

    def __init__(self, host, port, max_connections):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = None
        self.client_address = None
        self.max_connections = max_connections
        self.current_connections = 0
        self.lock = threading.Lock()
        self.server_running = False
        self.message_flags = self.convert_message_flags(self.load_message_flags())
        print(self.message_flags['INFO'])
        self.mac_address = None

        # Generowanie pary kluczy RSA
        self.rsa_key_pair = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        FileManager.save_keys_to_files(self.rsa_key_pair)

        self.restored_server_public_key = self.rsa_key_pair.public_key()


    def load_message_flags(self):

        flags_str = FileManager.read_json(join(dirname(abspath(__file__)), 'server_message_flags.json'))
        return flags_str
    
    def convert_message_flags(self, message_flags: dict):

        flags_bytes = {
            key: value.encode('utf-8') 
            for key, value in message_flags['flags'].items()
            }
        
        return flags_bytes


    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            print(f'Server listening on {self.host}:{self.port}...')

            self.server_running = True
            self.accept_connections()

        except socket.error as e:
            print(f"[ServerConnection.start_server] Error binding or starting the server: {e}")
            self.server_running = False

        except Exception as e:
            print(f"[ServerConnection.start_server] Unexpected error: {e}")


    def accept_connections(self):
        while self.server_running and self.current_connections < self.max_connections:
            try:
                self.client_socket, self.client_address = self.server_socket.accept()
                self.exchange_message_flags()
                choice = input(f'Would you like to accept connection from {self.client_address} - yes/no: ')

                if choice.lower() in ['yes', 'y']:
                    self.handle_client()
                else:
                    self.client_socket.sendall(b"Connection rejected by server..." + self.message_flags['INFO'])
                    self.client_socket.close()

            except socket.timeout as e:
                print(f"[ServerConnection.accept_connections] Socket timeout occurred: {e}")

            except socket.error as e:
                print(f"[ServerConnection.accept_connections] Socket error during connection acceptance: {e}")

            except Exception as e:
                print(f"[ServerConnection.accept_connections] Unexpected error: {e}")


    def handle_client(self):
        try:
            if self.current_connections < self.max_connections:
                self.current_connections += 1
                print(f'Connection with {self.client_address} accepted!')
                try:
                    self.client_socket.sendall(b"Connection accepted by server!" + self.message_flags['INFO'])
                except socket.error as e:
                    print(f"[ServerConnection.handle_client] Error sending connection accepted message: {e}")
            else:
                print(f'Connection with {self.client_address} rejected - connections limit reached!')
                try:
                    self.client_socket.sendall(b"Connection rejected by server!" + self.message_flags['INFO'])
                except socket.error as e:
                    print(f"[ServerConnection.handle_client] Error sending rejection message: {e}")
                finally:
                    self.client_socket.close()

        except Exception as e:
            print(f"[ServerConnection.handle_client] Unexpected error: {e}")


    def send_public_key(self):
        public_key_pem = self.rsa_key_pair.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.client_socket.sendall(public_key_pem + self.message_flags['END'])
        print("Public key sent to client.")

    def send_public_key_restored(self):
        # Używamy wczytanego klucza publicznego z pliku
        public_key_pem = self.restored_server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.client_socket.sendall(public_key_pem + self.message_flags['END'])
        print("Public key sent to client.")

    def receive_public_key(self, client_socket):
        client_public_key_pem = b""
        while True:
            chunk = client_socket.recv(1024)
            client_public_key_pem += chunk
            if b"-----END PUBLIC KEY-----" in client_public_key_pem:
                break
        client_public_key = serialization.load_pem_public_key(
            client_public_key_pem, backend=default_backend()
        )
        print("Client public key received.")
        return client_public_key


    def encrypt_with_public_key(self, public_key, aes_key):
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key


    def send_file_request(self, file_name: str, file_size: str, chunk_size: int):
        file_metadata = (f"File: {file_name}\nSize: {file_size} \nChunk: {str(chunk_size)} B").encode('utf-8') + self.message_flags['INFO']
        try:
            self.client_socket.sendall(file_metadata)
        except socket.error as e:
            print(f"[ServerConnection.send_file_request] Error sending file metadata: {e}")
        except Exception as e:
            print(f"[ServerConnection.send_file_request] Unexpected error: {e}")


    def send_EOF(self):
        try:
            self.client_socket.sendall(self.message_flags['END'] + self.message_flags['INFO'])
        except socket.error as e:
            print(f"[ServerConnection.send_EOF] Error sending EOF: {e}")
        except Exception as e:
            print(f"[ServerConnection.send_EOF] Unexpected error: {e}")


    def receive_answer(self):
        data = b""
        try:
            while self.server_running and not (self.message_flags['ACK'] in data or self.message_flags['RST'] in data):
                data += self.client_socket.recv(1)
                if not data:
                    break
            result = data.split(self.message_flags['INFO'])[0]
            if result == self.message_flags['ACK']:
                return True
            else:
                return False
        except socket.error as e:
            print(f"[ServerConnection.receive_answer] Error while receiving response: {e}")
        except Exception as e:
            print(f"[ServerConnection.receive_answer] Unexpected error: {e}")
        return False


    def send_file(self, file_data: bytes, chunk_size: int):
        if not isinstance(file_data, bytes):
            raise ValueError("file_data must be a bytes-like object.")
        try:
            print('Sending EOF flag...')

            self.send_EOF()
            print('Sending file...')
            for i in range(0, len(file_data), chunk_size):
                chunk = file_data[i:i + chunk_size]
                try:
                    self.client_socket.sendall(chunk)
                except socket.error as e:
                    print(f"[ServerConnection.send_file] Socket error while sending the file: {e}")
                except Exception as e:
                    print(f"[ServerConnection.send_file] An error occurred while sending the file: {e}")
            print('Done...')
        except Exception as e:
            print(f"[ServerConnection.send_file] Unexpected error: {e}")


    def exchange_message_flags(self):

        try:

            message_json = json.dumps(self.load_message_flags())
            self.client_socket.sendall(message_json.encode('utf-8') + b"/FLAGS/")
            print(f"Message flags have been sent to the client")
        
        except Exception as e:
            print(f'[ServerConnection.exchange_message_flags] An error occurred: {e}')


    def send_message(self, message):

        try:

            message_json = json.dumps(self.message_flags)
            self.client_socket.sendall(message_json.encode('utf-8') + self.message_flags['INFO'])
            print(f"Message sent to the client: {message_json}")
        
        except Exception as e:
            print(f'[ServerConnection.send_message] An error occurred: {e}')


    def stop_server(self):
        try:
            self.server_running = False
            self.server_socket.close()
            print("Server is stopped")
        except socket.error as e:
            print(f"[ServerConnection.stop_server] Error closing the server socket: {e}")
        except Exception as e:
            print(f"[ServerConnection.stop_server] Unexpected error: {e}")
