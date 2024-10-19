from connections.client import ClientConnection
from files.file_manager import FileManager
client = ClientConnection(host='127.0.0.1', port=1234)
client.connect_to_server()

if client.accept_file(b'/INFO/'):
    file = client.receive_file(1024)
    FileManager.save_file('', file, b'/END/')

else:
    exit()
