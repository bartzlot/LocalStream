from connections.client import ClientConnection
from files.file_manager import FileManager
from session.session_manager import SessionManager
from session.session_manager import get_mac_address
from session.session_manager import get_public_key

if __name__ == "__main__":

    choice = input("Do you want to restore your last saved session? (yes/no): ")

    if choice.lower() in ["yes", "y"]:
        # Przywracanie zapisanej sesji
        session_data = SessionManager.load_session()
        if session_data:
            print("Restoring saved session...")

            # Tworzenie klienta z zapisanymi danymi sesji
            client = ClientConnection(
                host=session_data["host"],
                port=session_data["port"]
            )

            # Podłączanie do serwera
            client.connect_to_server()
 
            try:
                # Ustawianie kluczy z sesji
                client.public_key = session_data["client_public_key"]
                server_public_key = session_data["server_public_key"]
                aes_key = session_data["aes_key"]
                client.mac_address = session_data["client_mac_address"]

                # Oczekiwanie na klucz publiczny serwera

                print("Waiting for server public key...")
                server_public_key_received = client.receive_public_key()
                client.send_public_key()

                # Sprawdzenie, czy klucz publiczny serwera jest zgodny z zapisanym w sesji
                if get_public_key(server_public_key_received) != get_public_key(server_public_key):
                    print("[Client] Server's public key does not match. Aborting session.")

                    exit()

                # Sprawdzenie, czy klient akceptuje żądanie pliku
                if client.accept_file():
                    file_data = client.receive_file(1024)
                    final_file_path = 'output2.txt'

                    # Zapisanie pliku
                    FileManager.save_file(final_file_path, file_data, b'/END/')

                    # Odszyfrowanie zapisanego pliku za pomocą klucza AES
                    FileManager.decrypt_file(final_file_path, aes_key)

                    print("File received and decrypted successfully.")

            except IOError as e:
                print(f"[Client] I/O error during file transfer or decryption: {e}")

            except Exception as e:
                print(f"[Client] An unexpected error occurred: {e}")
    else:
        # Inicjalizacja nowej sesji
        client = ClientConnection(host='127.0.0.1', port=1234)
        client.connect_to_server()
        client.mac_address = get_mac_address()

        try:
            # Odbiór klucza publicznego serwera i wysyłanie klucza publicznego klienta
            server_public_key = client.receive_public_key()
            client.send_public_key()

            print("Waiting for encrypted AES key...")
            encrypted_aes_key = client.client_socket.recv(256)  # Odbiór zaszyfrowanego klucza AES
            print(f"Encrypted AES key received: {encrypted_aes_key}")

            # Odszyfrowanie klucza AES za pomocą prywatnego klucza klienta
            aes_key = client.decrypt_with_private_key(encrypted_aes_key)
            print("AES key decrypted.")

            # Sprawdzenie, czy klient akceptuje żądanie pliku
            if client.accept_file():
                file_data = client.receive_file(1024)
                final_file_path = 'test_received.txt'

                # Zapisanie pliku
                FileManager.save_file(final_file_path, file_data,b'/END/')

                # Odszyfrowanie zapisanego pliku za pomocą klucza AES
                FileManager.decrypt_file(final_file_path, aes_key)

                # Zapisanie sesji
                save_session_choice = input("Do you want to save this session? (yes/no): ")
                if save_session_choice.lower() in ["yes", "y"]:
                    # Zapisanie sesji
                    SessionManager.save_session(
                        host=client.host,
                        port=client.port,
                        client_public_key=client.public_key,
                        server_public_key=server_public_key,
                        aes_key=aes_key,
                        file_name=final_file_path,
                        client_mac_address=get_mac_address()
                    )
                else:
                    print("Session not saved.")

            else:
                print("[Client] File request declined by server.")
                exit()

        except IOError as e:
            print(f"[Client] I/O error occurred during file transfer or decryption: {e}")
            exit()

        except Exception as e:
            print(f"[Client] An unexpected error occurred: {e}")
            exit()