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
        
        for conn in self.connections:
            print(f'{conn['ConnObj'].host}:{str(conn['ConnObj'].port)} - active: {conn['Status']}')

    
    def add_connection(self, ConnectionObj: object):

        conn_desc = {
            "ConnObj": ConnectionObj,
            "Status": True
        }

        self.connections.append(conn_desc)

    #TODO
    # def del_connection(self, ConnectionObj: object):

    #     for object in self.connections:

    #         if object.


        