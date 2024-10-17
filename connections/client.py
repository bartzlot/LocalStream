import socket
import threading
import time
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
            self.receive_data()

        except ConnectionRefusedError:

            print('Connecting failed!')
            self.client_socket.close()

    # def send_file(self, file_data, file_name):
    #     try:
    #         if self.connection_validator:
    #             # Kodowanie nazwy pliku
    #             file_name_bytes = file_name.encode('utf-8')
    #             file_name_length = str(len(file_name_bytes)).encode('utf-8')
                
    #             # Wysłanie długości nazwy pliku i nazwy pliku
    #             self.client_socket.sendall(file_name_length)  
    #             self.client_socket.sendall(file_name_bytes)  

    #             # Krótkie opóźnienie
    #             time.sleep(0.5)
                
    #             # Wysłanie długości danych pliku przed samym plikiem
    #             file_data_length = str(len(file_data)).encode('utf-8')
    #             self.client_socket.sendall(file_data_length)  # Wysłanie długości danych pliku
    #             self.client_socket.sendall(file_data)  # Wysłanie danych pliku

    #             print(f'Sent file data ({len(file_data)} bytes) to the server.')
    #         else:
    #             print("No active connection to send data.")
    #     except Exception as e:
    #         print(f"An error occurred while sending the file: {e}")

    # def close_connection(self):
    #     if self.connection_validator:
    #         self.connection_validator = False
    #         self.client_socket.close()
    #         print("Client connection closed.")

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
        # self.close_connection() 
        self.client_socket.close()

