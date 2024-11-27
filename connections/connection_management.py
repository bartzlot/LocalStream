import subprocess
import platform
import os
import netifaces
from typing import Dict
from connections.server import ServerConnection
from connections.client import ClientConnection
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from files.file_manager import FileManager, ErrorHandler

@dataclass
class Connection:
    server: ServerConnection
    active: bool

#Should be used to manage clients connected to the server
class ServerConnectionsManager:

    @staticmethod
    def get_private_ip():

        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addresses:
                for addr_info in addresses[netifaces.AF_INET]:
                    ip_address = addr_info['addr']
                    if ip_address != '127.0.0.1':
                        return ip_address
                    
        return None


    def __init__(self):

        self.connections: Dict[int, Connection] = {}
        self.ovrl_conn_amount = 0
        self.active_conn_amount = 0
        self.inactive_conn_amount = 0
        self.executor = ThreadPoolExecutor(max_workers=10)

    def __str__(self):

        result = "Server Connections:\n"
        result += "-" * 50 + "\n"
        result += f"{'Host':<20}{'Port':<10}{'Status':<10}\n"
        result += "-" * 50 + "\n"
        for port, conn in self.connections.items():
            status = "Active" if conn.active else "Inactive"
            result += f"{conn.server.host:<20}{port:<10}{status:<10}\n"
        result += "-" * 50 + "\n"
        result += f"Overall Connections: {self.ovrl_conn_amount}\n"
        result += f"Active Connections: {self.active_conn_amount}\n"
        result += f"Inactive Connections: {self.inactive_conn_amount}\n"

        return result

    def add_connection(self, host: str, port: int, max_connections: int):

        if port not in self.connections:

            connection = ServerConnection(host, port, max_connections)
            conn_desc = Connection(server=connection, active=True)
            self.connections[port] = conn_desc
            self.executor.submit(connection.start_server)
            self.ovrl_conn_amount += 1
            self.active_conn_amount += 1

            return f"Server started and listening on {host}:{port}"
        
        else:
            return f"Server already running on port {port}"

    def del_connection(self, port: int):

        if port in self.connections:

            conn = self.connections.pop(port)
            conn.server.stop_server()
            print(f"Deleted connection: {conn.server.host}:{port}")
            self.active_conn_amount -= 1

        else:
            print("There is no connection on this port")

    def send_file(self, port: int, file_path: str, chunk_size: int = 1024):

        if port in self.connections:
            self.executor.submit(self._send_file_thread, port, file_path, chunk_size)
        else:
            print(f"No active connection on port {port}")

    def _send_file_thread(self, port: int, file_path: str, chunk_size: int):
        conn = self.connections[port]
        try:
            # Key exchange
            conn.server.send_public_key()
            print("Public key sent to client.")
            client_public_key = conn.server.receive_public_key(conn.server.client_socket)
            print("Client public key received.")
            # Generate AES key
            aes_key = os.urandom(32)  # 256-bit AES key
            encrypted_aes_key = conn.server.encrypt_with_public_key(client_public_key, aes_key)

            # Send encrypted AES key
            conn.server.client_socket.sendall(encrypted_aes_key + conn.server.message_flags['END'])

            # Encrypt file
            encrypted_file_path = FileManager.encrypt_file(file_path, aes_key)

            file_data = FileManager.read_file(encrypted_file_path, chunk_size, conn.server.message_flags['END'])
            conn.server.send_file_request(file_data[1], file_data[1], chunk_size)

            if conn.server.receive_answer():
                conn.server.send_file(file_data[0], chunk_size)
                FileManager.delete_file(encrypted_file_path)
            else:
                print(f"Client rejected the file transfer request for {file_data[1]}.")

        except FileNotFoundError:
            print(f"File {file_path} not found.")
        except Exception as e:
            print(f"Error sending file: {e}")

    @staticmethod
    def possible_connections():

        try:

            system = platform.system().lower

            if system == 'darwin' or 'linux':
                cmd = "netstat -nr | grep UHLWI | grep -E '^([0-9]{1,3}\\.){3}[0-9]{1,3}' | awk '{print $1 \"-\" $2}'"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            possible_conns = []

            for line in result.stdout.split('\n'):
                conn = line.split('-')
                if len(conn) == 2:
                    possible_conns.append({'host_ip': conn[0], 'host_mac': conn[1]})

            return possible_conns

        except subprocess.SubprocessError as e:
            print(f"Error getting network devices: {e}")
            return []

        except Exception as e:
            print(f'An error has occurred during search for possible connections: {e}')
            return []

    def list_possible_connections(self):

        possible_conns = ServerConnectionsManager.possible_connections()
        result = "Possible Connections:\n"
        result += "-" * 50 + "\n"
        result += f"{'Host IP':<20}{'Host MAC':<30}\n"
        result += "-" * 50 + "\n"
        if possible_conns:
            for conn in possible_conns:
                result += f"{conn['host_ip']:<20}{conn['host_mac']:<30}\n"
        else:
            result += "No possible connections found.\n"
        result += "-" * 50 + "\n"
        print(result)


class ClientConnectionsManager:

    def __init__(self):
        
        self.client_connection = None
        self.executor = ThreadPoolExecutor(max_workers=10)

    def connect_to_server(self, host, port):

        try:

            self.client_connection = ClientConnection(host, port)
            self.client_connection.connect_to_server()

        except Exception as e:
            print(f"Error connecting to the server: {e}")
            self.client_connection.client_socket.close()

    def receive_file(self, save_path: str, chunk_size=1024):
            
            try:
                # Key exchange
                print("Waiting for server public key...")
                server_public_key = self.client_connection.receive_public_key()
                self.client_connection.send_public_key()

                print("Waiting for encrypted AES key...")
                encrypted_aes_key = self.client_connection.client_socket.recv(256) 
                print('Encrypted AES key received...')

                aes_key = self.client_connection.decrypt_with_private_key(encrypted_aes_key)
                print("AES key decrypted.")

                # Accept file transfer
                if self.client_connection.accept_file():
                    file_data = self.client_connection.receive_file(chunk_size)

                    if file_data:
                        # Save the received file
                        FileManager.save_file(save_path, file_data, self.client_connection.message_flags['END'])
                        print(f"File received and saved as {save_path}")
                        FileManager.decrypt_file(save_path, aes_key)

                    else:
                        print("Failed to receive file.")
                else:
                    print("File transfer rejected.")
            except Exception as e:
                ErrorHandler.error_handling("receive_file", e)

    

            



