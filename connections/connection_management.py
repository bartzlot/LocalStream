import subprocess
import platform
import os

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

    @staticmethod
    def possible_connections():

        try:

            system = platform.system().lower

            if system == 'darwin' or 'linux':
                cmd = "netstat -nr | grep UHLWI | grep -E '^([0-9]{1,3}\.){3}[0-9]{1,3}' | awk '{print $1 \"-\" $2}'"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
            possible_conns = []

            for line in result.stdout.split('\n'):

                conn = line.split('-')

                if len(conn) == 2:

                    possible_conns.append({'host_ip': conn[0],
                                            'host_mac': conn[1]})
  
            return possible_conns
        
        except subprocess.SubprocessError as e:

            print(f"Error getting network devices: {e}")
            return []
        
        except Exception as e:

            print(f'An error has occured during search for possible connections: {e}')
            return []


    

            



