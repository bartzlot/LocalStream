import socket
import threading

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


    def stop_server(self):

        self.server_running = False
        self.server_socket.close()
        print("Server is stopped")