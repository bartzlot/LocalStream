from connections.client import ClientConnection

client = ClientConnection(host='127.0.0.1', port=1234)
client.connect_to_server()
file = client.receive_file(1024, b'/END/')
print(file)