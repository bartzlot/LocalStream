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
            self.receive_data(b"/INFO/")

        except ConnectionRefusedError:

            print('Connecting failed!')
            self.client_socket.close()


    def receive_file(self, chunk_size: int, EOF_flag: bytes):

        file_data = bytearray()
        chunk = b''

        while EOF_flag not in chunk:

            chunk = self.client_socket.recv(chunk_size)
            file_data += chunk

        return file_data

    # def close_connection(self):
    #     if self.connection_validator:
    #         self.connection_validator = False
    #         self.client_socket.close()
    #         print("Client connection closed.")

    def receive_data(self, INFO_flag: bytes):

        data = b""

        while self.connection_validator and INFO_flag not in data:

            try:

                data += self.client_socket.recv(1)

                if not data:
                    break     

            except ConnectionRefusedError:
                print(f'Connection with server got closed!')
                self.connection_validator = False
        
        print(f'Received from server: {data.split(INFO_flag)[0].decode()}') 


