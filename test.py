from connections.client import ClientConnection
from files.file_manager import FileManager

if __name__ == "__main__":
    client = ClientConnection(host='127.0.0.1', port=1234)
    client.connect_to_server()

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
        if client.accept_file(b'/INFO/'):
            file_data = client.receive_file(1024)
            final_file_path = ''

            # Zapisanie pliku
            FileManager.save_file(final_file_path, file_data, b'/END/')

            # Odszyfrowanie zapisanego pliku za pomocą klucza AES
            FileManager.decrypt_file(final_file_path, aes_key)
        else:
            print("[Client] File request declined by server.")
            exit()

    except IOError as e:
        print(f"[Client] I/O error occurred during file transfer or decryption: {e}")
        exit()

    except Exception as e:
        print(f"[Client] An unexpected error occurred: {e}")
        exit()
