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
    
    
    file_path = "/Users/bartzlot/Programming/LocalStream/cat.txt"
    file_data = FileManager.read_file(file_path, 1024, b'/END/')

    server.send_file_request(file_data[1], file_data[2], 1024, b'/INFO/')

    if server.receive_answer(b'/INFO/'):
        server.send_file(file_data[0], 1024)
    
    else:
        server.stop_server()

        

