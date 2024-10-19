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

            print('Connecting failed!')
            self.client_socket.close()


    def accept_file(self, INFO_flag: bytes):

        data = b""

        while self.connection_validator and INFO_flag not in data:

            try:

                data += self.client_socket.recv(1)

                if not data:
                    break     

            except ConnectionRefusedError:
                print(f'Connection with server got closed!')
                self.connection_validator = False
        
        print(f'Would you like to accept transfer of:\n {data.split(INFO_flag)[0].decode()}')
        choice  = input('yes/no: ')

        if choice.lower() in ['yes', 'y']:

            self.client_socket.sendall(b"/ACK/" + INFO_flag)
            return True

        elif choice.lower() in ['no', 'n']:

            self.client_socket.sendall(b"/RST/" + INFO_flag)
            return False
        
        else:

            self.client_socket.sendall(b"/RST/" + INFO_flag)
            return False


    def receive_file(self, chunk_size: int):

        EOF_flag = self.receive_EOF_flag(b'/INFO/')
        file_data = bytearray()
        chunk = b''

        while EOF_flag not in chunk:

            chunk = self.client_socket.recv(chunk_size)
            file_data += chunk

        return file_data


    def receive_EOF_flag(self, INFO_flag: bytes):

        data = b""

        while self.connection_validator and INFO_flag not in data: 

            try:

                data += self.client_socket.recv(1)

                if not data:
                    break     

            except ConnectionRefusedError:
                print(f'Connection with server got closed!')
                self.connection_validator = False

        return data.split(INFO_flag)[0]


    def receive_messages(self, INFO_flag: bytes):

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


