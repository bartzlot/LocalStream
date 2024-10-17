import socket
import threading
import os

class ServerConnection:

    def __init__(self, host, port, max_connections):
        
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.max_connections = max_connections
        self.current_connections = 0
        self.lock = threading.Lock()
        self.server_running = False
        
    
    def start_server(self):

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_connections)
        print(f'Server listening on {self.host}:{self.port}...')

        self.server_running = True
        threading.Thread(target=self.accept_connections).start()


    def accept_connections(self):

        while self.server_running:

            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
            
            except socket.error:
                #TODO
                pass

    
    def handle_client(self, client_socket, client_address):

        with self.lock:

            if self.current_connections < self.max_connections:

                self.current_connections += 1
                print(f'Connection with {client_address} accepted!')
                client_socket.sendall(b"Connection accepted by server!")

            else:

                print(f'Connection with {client_address} rejected - connections limit reached!')
                client_socket.sendall(b"Connection rejected by server!")
                client_socket.close()

                return
        # try:
        #     file_data, file_name = self.receive_file(client_socket)
        #     if file_data:
        #         print(f"Received file '{file_name}' ({len(file_data)} bytes) from {client_address}.")
        #         self.save_file(file_data, file_name)  # Zapisujemy otrzymany plik
        #     else:
        #         print("No file data received.")

        # except Exception as e:
        #     print(f"An error occurred while handling the client {client_address}: {e}")

        # finally:
        #     with self.lock: 
        #         self.current_connections -= 1

        # client_socket.close()
        # print(f'Connection with {client_address} closed.')

    # def receive_file(self, client_socket):
    #     try:
    #         client_socket.settimeout(10)  # Ustawienie timeoutu na 10 sekund
            
    #         # Odbieranie długości nazwy pliku
    #         file_name_length = int(client_socket.recv(1024).decode('utf-8'))
    #         file_name = client_socket.recv(file_name_length).decode('utf-8')

    #         # Odbieranie długości danych pliku
    #         file_data_length = int(client_socket.recv(1024).decode('utf-8'))
            
    #         # Odbieranie danych pliku
    #         file_data = b""
    #         while len(file_data) < file_data_length:
    #             data = client_socket.recv(1024)
    #             if not data:
    #                 break
    #             file_data += data

    #         return file_data, file_name
    #     except Exception as e:
    #         print(f"An error occurred while receiving the file: {e}")
    #         return b"", ""



    # def save_file(self, file_data, file_name):
    #     desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", file_name)
    #     with open(desktop_path, 'wb') as file:
    #         file.write(file_data)
    #         print(f"File saved as: {desktop_path}")
        
    def stop_server(self):

        self.server_running = False
        self.server_socket.close()
        print("Server is stopped")