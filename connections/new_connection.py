import ipaddress

def get_connection_info():

    run_menu = True
    while run_menu:

        addr_port = input('Insert valid IP address and PORT ("IP:PORT"): ')
        ip_address, port = addr_port.split(':')

        if validate_ip(ip_address) and validate_port(port):
            run_menu = False
            return (ip_address, int(port))
        

def validate_ip(ip_addr: str):

    try:
        ipaddress.ip_address(ip_addr)
    
    except:
        print("Provide valid IP address e.g. (X.X.X.X)...")
        return False
    
    return True


def validate_port(port: str):

    try:
        
        if int(port) > 1025 and int(port) < 65535:
            return True
        
        else:

            print("Provide port number between 1025-65535...")
            return False
        
    except:
        
        print("You have to provide a integer number...")
        return False