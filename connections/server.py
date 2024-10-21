import socket
import threading
import os

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
        
    
    def start_server(self):
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            print(f'Server listening on {self.host}:{self.port}...')

            self.server_running = True
            self.accept_connections(b"/INFO/")

        except socket.error as e:
            print(f"[ServerConnection.start_server] Error binding or starting the server: {e}")
            self.server_running = False

        except Exception as e:
            print(f"[ServerConnection.start_server] Unexpected error: {e}")


    def accept_connections(self, INFO_flag: bytes):

        while self.server_running and self.current_connections < self.max_connections:
            try:
                self.client_socket, self.client_address = self.server_socket.accept()
                choice  = input(f'Would you like to accept connection from {self.client_address} - yes/no: ')

                if choice.lower() in ['yes', 'y']:
                    self.handle_client(b"/INFO/")

                else:                   
                    self.client_socket.sendall(b"Connection rejected by server..." + INFO_flag)
                    self.client_socket.close()

            except socket.timeout as e:
                print(f"[ServerConnection.accept_connections] Socket timeout occurred: {e}")

            except socket.error as e:
                print(f"[ServerConnection.accept_connections] Socket error during connection acceptance: {e}")

            except Exception as e:
                print(f"[ServerConnection.accept_connections] Unexpected error: {e}")

    
    def handle_client(self, INFO_flag: bytes):

        try:
            if self.current_connections < self.max_connections:
                    if self.current_connections < self.max_connections:

                        self.current_connections += 1
                        print(f'Connection with {self.client_address} accepted!')
                        try:
                            self.client_socket.sendall(b"Connection accepted by server!" + INFO_flag)

                        except socket.error as e:
                            print(f"[ServerConnection.handle_client] Error sending connection accepted message: {e}")

                        return
                    
                    else:
                        print(f'Connection with {self.client_address} rejected - connections limit reached!')

                        try:
                            self.client_socket.sendall(b"Connection rejected by server!" + INFO_flag)
                        except socket.error as e:
                           
                           print(f"[ServerConnection.handle_client] Error sending rejection message: {e}")

                        finally:
                            self.client_socket.close()

        except Exception as e:
            print(f"[ServerConnection.handle_client] Unexpected error: {e}")

    def send_file_request(self, file_name: str, file_size: str, chunk_size: int, INFO_flag: bytes):

        file_metadata = (f"File: {file_name}\nSize: {file_size} Mb\nChunk: {str(chunk_size)} B").encode('utf-8') + INFO_flag

        try:
            self.client_socket.sendall(file_metadata)

        except socket.error as e:
            print(f"[ServerConnection.send_file_request] Error sending file metadata: {e}")

        except Exception as e:
            print(f"[ServerConnection.send_file_request] Unexpected error: {e}")
    
    def send_EOF(self, EOF_flag: bytes, INFO_flag: bytes):

        try:
            self.client_socket.sendall(EOF_flag + INFO_flag)

        except socket.error as e:
            print(f"[ServerConnection.send_EOF] Error sending EOF: {e}")

        except Exception as e:
            print(f"[ServerConnection.send_EOF] Unexpected error: {e}")

    def receive_answer(self, INFO_flag: bytes):

        data = b""

        try:
            while self.server_running and not (b"/ACK/" in data or b"/RST/" in data):
                try:
                    data += self.client_socket.recv(1)
                    if not data:
                        break     
                except ConnectionRefusedError:
                    print(f"[ServerConnection.receive_answer] Connection with server got closed!")
                    self.server_running = False 

            result = data.split(b'/INFO/')[0]           
            if result == b"/ACK/":
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
            self.send_EOF(b'/END/', b'/INFO/')
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

    def stop_server(self):

        try:
            self.server_running = False
            self.server_socket.close()
            print("Server is stopped")
        except socket.error as e:
            print(f"[ServerConnection.stop_server] Error closing the server socket: {e}")
        except Exception as e:
            print(f"[ServerConnection.stop_server] Unexpected error: {e}")
        