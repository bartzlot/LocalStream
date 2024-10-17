# from .client import 
from connections.server import ServerConnection
from connections.client import ClientConnection
from files.file_manager import FileManager 
if __name__ == "__main__":

    # Start the server
    server = ServerConnection(host='127.0.0.1', port=1234, max_connections=1)
    server.start_server()

    # Start the client and connect to the server    
    client = ClientConnection(host='127.0.0.1', port=1234)


    client.connect_to_server()

    # Load a file from the local filesystem
    file_path = r"d:\Users\SUPERKOMP\Desktop\TEST.txt"
    file_data = FileManager.read_file(file_path)

    # Send the file to the server if loaded
    if file_data:
        client.send_file(file_data, "TEST.txt")
        print("File sent to the server.")

    # Give the server time to process the file
    input("Press Enter to stop the server...")  # Wait for user input before stopping the server

    server.stop_server()
