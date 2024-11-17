import fire
from connections.connection_management import ServerConnectionsManager

class CLI:
    def __init__(self):
        self.server_manager = ServerConnectionsManager()
        self.running = True

    def add_connection(self, host, port, max_connections):
        return self.server_manager.add_connection(host, port, max_connections)

    def del_connection(self, port):
        return self.server_manager.del_connection(port)
    
    def send_file(self, port, file_path, chunk_size=1024):
        return self.server_manager.send_file(port, file_path, chunk_size)
    
    def possible_connections(self):
        return self.server_manager.list_possible_connections()

    def status(self):
        return str(self.server_manager)
    
    def exit(self):
        self.running = False
        return "Exiting CLI..."

if __name__ == '__main__':
    cli = CLI()
    while cli.running:
        command = input("Enter command: ").strip().split()
        if command:
            try:
                fire.Fire(cli, command)
            except SystemExit:
                pass