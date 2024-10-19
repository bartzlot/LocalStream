import threading
import socket

#Should be used to manage clients connected to the server
class ServerConnectionsManager:

    def __init__(self):

        self.connections = []
        self.ovrl_conn_amount = 0
        self.active_conn_amount = 0
        self.inactive_conn_amount = 0


    def __str__(self):
        
        result = ''

        for conn in self.connections:
            result += f'{conn['ConnObj'].host}:{str(conn['ConnObj'].port)} - active: {conn['Status']}\n'

        return result

    
    def add_connection(self, ConnectionObj: object):

        conn_desc = {
            "ConnObj": ConnectionObj,
            "Status": True
        }

        self.connections.append(conn_desc)


    def del_connection(self, ConnectionObj: object):
            
        if ConnectionObj in self.connections :
            
            print(f"Deleted connection: {ConnectionObj.host}:{str(ConnectionObj['ConnObj'].port)}")
            self.connections.remove(ConnectionObj)
            
        else:
            print("There is no connection like this...")
            



