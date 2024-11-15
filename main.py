from os.path import join, dirname, abspath
from connections.server import ServerConnection
from connections.client import ClientConnection
from files.error_handler import ErrorHandler
from connections.connection_management import ServerConnectionsManager
from files.file_manager import FileManager
import os
from session.session_manager import SessionManager
from session.session_manager import get_mac_address
from session.session_manager import get_public_key


if __name__ == "__main__":

    choice = input("Do you want to restore your last saved session? (yes/no): ")

    # Jeśli użytkownik wybiera przywrócenie sesji
    if choice.lower() in ["yes", "y"]:
        # Przywracanie zapisanej sesji
        session_data = SessionManager.load_session_server()
        if session_data:
            print("Restoring saved session...")

            # Tworzenie serwera z zapisanymi danymi sesji
            server_manager = ServerConnectionsManager()
            server = ServerConnection(
                host=session_data["host"], port=session_data["port"], max_connections=1
            )
            server_manager.add_connection(server)
            server.start_server()

            # Ustawianie zmiennych sesji
            client_public_key = session_data["client_public_key"]
            server_public_key = session_data["server_public_key"]
            aes_key = session_data["aes_key"]
            server.restored_server_public_key = server_public_key
            server.mac_address = session_data["server_mac_address"]

            print("Sending public key to client...")
            server.send_public_key_restored()

            print("Waiting for client public key...")
            client_public_key_received = server.receive_public_key(server.client_socket)

            # Sprawdzenie, czy klucz publiczny klienta się zgadza
            if get_public_key(client_public_key_received) != get_public_key(
                client_public_key
            ):
                print("[Server] Client's public key does not match. Aborting session.")
                server.stop_server()
                exit()

            file_path = "input2.txt"  # Możliwość zmiany pliku

            # Szyfrowanie pliku
            enc_file_path = FileManager.encrypt_file(file_path, aes_key)
            if enc_file_path:
                file_data = FileManager.read_file(enc_file_path, 1024, b"/END/")
            else:
                raise Exception(f"Error during file encryption: {file_path}")

            # Sprawdzenie, czy klient jest połączony
            if server.client_socket:
                # Wysłanie żądania pliku do klienta
                server.send_file_request(file_data[1], file_data[2], 1024)

                if server.receive_answer():
                    # Wysłanie zaszyfrowanego pliku do klienta
                    server.send_file(file_data[0], 1024)
                    FileManager.delete_file(enc_file_path)
                else:
                    print("[Main] Client declined the file request.")
                    server.stop_server()
            else:
                print("[Main] No client connected.")
                server.stop_server()
    else:

        # Jeśli użytkownik nie wybiera przywrócenia sesji, rozpoczynamy nową
        server_manager = ServerConnectionsManager()
        server = ServerConnection(host="127.0.0.1", port=1234, max_connections=1)
        server_manager.add_connection(server)
        server.start_server()
        server.mac_address = get_mac_address()

        try:
            file_path = "input.txt"

            # Generowanie klucza AES
            aes_key = os.urandom(32)

            # Szyfrowanie pliku
            enc_file_path = FileManager.encrypt_file(file_path, aes_key)
            if enc_file_path:
                file_data = FileManager.read_file(
                    enc_file_path, 1024, server.message_flags["END"]
                )
            else:
                raise Exception(f"Error during file encryption: {file_path}")

        except Exception as e:
            ErrorHandler.error_handling("File_encryption", e)
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
                    encrypted_aes_key = server.encrypt_with_public_key(
                        client_public_key, aes_key
                    )
                    print("Sending encrypted AES key to client...")
                    server.client_socket.sendall(encrypted_aes_key)

                    # Wysłanie żądania pliku do klienta
                    server.send_file_request(file_data[1], file_data[2], 1024)

                    if server.receive_answer():
                        # Wysłanie zaszyfrowanego pliku do klienta
                        server.send_file(file_data[0], 1024)
                        FileManager.delete_file(enc_file_path)
                        # Zapisanie sesji po zakończeniu transferu
                        save_session_choice = input(
                            "Do you want to save this session? (yes/no): "
                        )
                        if save_session_choice.lower() in ["yes", "y"]:
                            # Zapisanie sesji
                            SessionManager.save_session_server(
                                host=server.host,
                                port=server.port,
                                client_public_key=client_public_key,
                                server_public_key=server.rsa_key_pair.public_key(),
                                aes_key=aes_key,
                                file_name=file_path,
                                server_mac_address=get_mac_address(),
                            )
                        else:
                            print("Session not saved.")

                    else:
                        print("[Main] Client declined the file request.")
                        server.stop_server()

                except Exception as e:
                    ErrorHandler.error_handling("Main", e)
                    server.stop_server()

            else:
                print("[Main] No client connected.")
                server.stop_server()

    parent_dir = dirname(abspath(__file__))
    priv_dir = join(parent_dir, ".private_keys")
    public_dir = join(parent_dir, ".public_keys")

    FileManager.delete_file(join(public_dir, "c_public_key.pem"))
    FileManager.delete_file(join(priv_dir, "c_private_key.pem"))
    FileManager.delete_file(join(public_dir, "s_public_key.pem"))
    FileManager.delete_file(join(priv_dir, "s_private_key.pem"))
