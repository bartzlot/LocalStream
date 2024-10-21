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
    
    try:
        file_path = ""
        file_data = FileManager.read_file(file_path, 1024, b'/END/')

    except FileNotFoundError:
        print(f"[Main] Error: The file '{file_path}' was not found. Please check the file path and try again.")
        server.stop_server()
    
    except IOError as e:
        print(f"[Main] Error: An I/O error occurred while reading the file: {e}")
        server.stop_server()
    
    except ValueError:
        print(f"[Main] Error: Invalid file path provided. Please ensure the file path is correct.")
        server.stop_server()
    
    except TypeError as e:
        print(f"[Main] Error: Type error occurred while reading the file - {e}. Please check the arguments passed.")
        server.stop_server()
    
    except Exception as e:
        print(f"[Main] An unexpected error occurred while reading the file: {e}")
        server.stop_server()
 
    else:
        server.send_file_request(file_data[1], file_data[2], 1024, b'/INFO/')

        if server.receive_answer(b'/INFO/'):
            server.send_file(file_data[0], 1024)
        
        else:
            server.stop_server()

        

