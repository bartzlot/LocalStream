# from .client import 
from connections.server import ServerConnection
from connections.client import ClientConnection
from connections.connection_management import ServerConnectionsManager

if __name__ == "__main__":


    server_manager = ServerConnectionsManager()
    server = ServerConnection(host='127.0.0.1', port=1234, max_connections=1)
    server_manager.add_connection(server)
    server.start_server()
    print(server_manager)
    # server.stop_server()