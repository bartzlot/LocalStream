# from .client import 
from connections.server import ServerConnection
from connections.client import ClientConnection


if __name__ == "__main__":

    server = ServerConnection(host='127.0.0.1', port=1234, max_connections=1)
    server.start_server()
    # server.stop_server()