import socket
import threading
from files.file_manager import FileManager

class ClientConnection():

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_validator = False

    
    def connect_to_server(self):

        try:
            self.client_socket.connect((self.host, self.port))
            print(f'Connecting to {self.host}:{self.port}')
            self.connection_validator = True
            self.receive_messages(b"/INFO/")
        
        except ConnectionRefusedError:
            print(f'[ClientConnection.connect_to_server] Connection failed! The server is unavailable or refused the connection.')
            self.client_socket.close()

        except OSError as e:
            print(f'[ClientConnection.connect_to_server] OS error occurred: {e}')
            self.client_socket.close()

        except Exception as e:
            print(f'[ClientConnection.connect_to_server] An unexpected error occurred: {e}')
            self.client_socket.close()
            
    def accept_file(self, INFO_flag: bytes):

        data = b""

        try:
            while self.connection_validator and INFO_flag not in data:
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

        print(f'Would you like to accept transfer of:\n {data.split(INFO_flag)[0].decode()}')
        choice  = input('yes/no: ')

        try:
            if choice.lower() in ['yes', 'y']:
                self.client_socket.sendall(b"/ACK/" + INFO_flag)
                return True

            elif choice.lower() in ['no', 'n']:
                self.client_socket.sendall(b"/RST/" + INFO_flag)
                return False
            
            else:
                self.client_socket.sendall(b"/RST/" + INFO_flag)
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
            EOF_flag = self.receive_EOF_flag(b'/INFO/')
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

    def receive_EOF_flag(self, INFO_flag: bytes):

        data = b""

        try:
            while self.connection_validator and INFO_flag not in data: 
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
        return data.split(INFO_flag)[0]


    def receive_messages(self, INFO_flag: bytes):

        data = b""
        
        try:
            while self.connection_validator and INFO_flag not in data:
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
        
        print(f'Received from server: {data.split(INFO_flag)[0].decode()}') 


