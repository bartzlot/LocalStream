from connections.server import ServerConnection
from connections.client import ClientConnection
from connections.connection_management import ServerConnectionsManager
from files.file_manager import FileManager
import os

if __name__ == "__main__":
    server_manager = ServerConnectionsManager()
    server = ServerConnection(host='127.0.0.1', port=1234, max_connections=1)
    server_manager.add_connection(server)
    server.start_server()

    try:
        file_path = "input.txt"

        # Generowanie klucza AES
        aes_key = os.urandom(32)

        # Szyfrowanie pliku
        enc_file_path = FileManager.encrypt_file(file_path, aes_key)
        if enc_file_path:
            file_data = FileManager.read_file(enc_file_path, 1024, b'/END/')
        else:
            raise Exception(f"Error during file encryption: {file_path}")

    except FileNotFoundError:
        print(f"[Main] Error: The file '{file_path}' was not found. Please check the file path and try again.")
        server.stop_server()

    except IOError as e:
        print(f"[Main] Error: An I/O error occurred while handling the file: {e}")
        server.stop_server()

    except ValueError:
        print(f"[Main] Error: Invalid file path provided. Please ensure the file path is correct.")
        server.stop_server()

    except TypeError as e:
        print(f"[Main] Error: Type error occurred while handling the file - {e}. Please check the arguments passed.")
        server.stop_server()

    except Exception as e:
        print(f"[Main] An unexpected error occurred: {e}")
        server.stop_server()

    else:
        # Sprawdzenie, czy klient jest połączony
        if server.client_socket:
            try:
                print("Sending public key to client...")
                server.send_public_key()

                # Odbiór klucza publicznego klienta
                client_public_key = server.receive_public_key(server.client_socket)

                # Szyfrowanie klucza AES kluczem publicznym klienta
                encrypted_aes_key = server.encrypt_with_public_key(client_public_key, aes_key)
                print("Sending encrypted AES key to client...")
                server.client_socket.sendall(encrypted_aes_key)

                # Wysłanie żądania pliku do klienta
                server.send_file_request(file_data[1], file_data[2], 1024, b'/INFO/')

                if server.receive_answer(b'/INFO/'):
                    # Wysłanie zaszyfrowanego pliku do klienta
                    server.send_file(file_data[0], 1024)
                    FileManager.delete_file(enc_file_path)

                else:
                    print("[Main] Client declined the file request.")
                    server.stop_server()

            except IOError as e:
                print(f"[Main] Error: I/O error occurred during client-server communication: {e}")
                server.stop_server()

            except Exception as e:
                print(f"[Main] An unexpected error occurred during client-server communication: {e}")
                server.stop_server()

        else:
            print("[Main] No client connected.")
            server.stop_server()

    FileManager.delete_file('c_public_key.pem')
    FileManager.delete_file('c_private_key.pem')
    FileManager.delete_file('s_public_key.pem')
    FileManager.delete_file('s_private_key.pem')