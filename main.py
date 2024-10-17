# from .client import 
from connections.server import ServerConnection
from connections.client import ClientConnection
from connections.connection_management import ServerConnectionsManager
from files.file_manager import FileManager 


if __name__ == "__main__":


    server_manager = ServerConnectionsManager()
    server = ServerConnection(host='127.0.0.1', port=1234, max_connections=1)
    server_manager.add_connection(server)
    server.start_server()
    print(server_manager)
    
    file_path = ""
    file_data = FileManager.read_file(file_path)

    if file_data:
        client.send_file(file_data, "TEST.txt")
        print("File sent to the server.")
        

