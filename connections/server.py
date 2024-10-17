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
        self.accept_connections()
        input()


    def accept_connections(self):

        while self.server_running:

            try:
                client_socket, client_address = self.server_socket.accept()

                choice  = input(f'Would you like to accept connection from {client_address} - yes/no: ')

                if choice.lower() in ['yes', 'y']:
                    self.handle_client(client_socket, client_address)
                
                else: 
                    
                    client_socket.sendall(b"Connection rejected by server")
                    client_socket.close()
            
            except socket.error:
                #TODO
                pass

    
    def handle_client(self, client_socket, client_address):

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

        