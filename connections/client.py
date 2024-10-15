import socket
import threading

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
            threading.Thread(target=self.receive_data).start()  

        except ConnectionRefusedError:

            print('Connecting failed!')
            self.client_socket.close()

    def receive_data(self):

        while self.connection_validator:

            try:
                data = self.client_socket.recv(1024)

                if not data:
                    break

                print(f'Received from server: {data.decode()}')      

            except ConnectionRefusedError:
                print(f'Connection with server got closed!')
                self.connection_validator = False
        
        self.client_socket.close()

