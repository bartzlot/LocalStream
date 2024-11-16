from files.file_manager import FileManager
from cryptography.hazmat.primitives import serialization
import uuid

def get_public_key(key):
    public_key_pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return public_key_pem


def get_mac_address():
    mac = uuid.getnode()
    mac_address = ':'.join([f'{(mac >> i) & 0xff:02x}' for i in range(0, 8 * 6, 8)][::-1])
    return mac_address

class SessionManager:


    @staticmethod
    def save_session(host, port, client_public_key, server_public_key, aes_key, file_name, client_mac_address):
        session_data = {
            "host": host,
            "port": port,
            "client_mac_address": client_mac_address,
            "client_public_key": client_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),  # Serializacja do formatu PEM
            "server_public_key": server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),
            "aes_key": aes_key.hex(),  # Klucz AES zapisany w formie hex
            "file_name": file_name
        }
        # Zapis do pliku JSON
        FileManager.save_session_file(session_data, 'session.json')

    def save_session_server(host, port, client_public_key, server_public_key, aes_key, file_name, server_mac_address):

        session_data = {
            "host": host,
            "port": port,
            "server_mac_address": server_mac_address,
            "client_public_key": client_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),  # Serializacja do formatu PEM
            "server_public_key": server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),
            "aes_key": aes_key.hex(),  # Klucz AES zapisany w formie hex
            "file_name": file_name
        }
        # Zapis do pliku JSON
        FileManager.save_session_file(session_data, 'session_server.json')

    @staticmethod
    def load_session():

        try:
            session_data = FileManager.load_session_file('session.json')
            # Przywracanie danych sesji z pliku
            client_public_key = serialization.load_pem_public_key(
                session_data["client_public_key"].encode('utf-8')
            )
            server_public_key = serialization.load_pem_public_key(
                session_data["server_public_key"].encode('utf-8')
            )
            aes_key = bytes.fromhex(session_data["aes_key"])

            return {
                "host": session_data["host"],
                "port": session_data["port"],
                "client_mac_address": session_data["client_mac_address"],
                "client_public_key": client_public_key,
                "server_public_key": server_public_key,
                "aes_key": aes_key,
                "file_name": session_data["file_name"]
            }

        except Exception as e:
            print(f"[SessionManager.load_session] Błąd przy wczytywaniu sesji: {e}")
            return None

    @staticmethod
    def load_session_server():

        try:

            session_data = FileManager.load_session_file('session_server.json')
            # Przywracanie danych sesji z pliku
            client_public_key = serialization.load_pem_public_key(
                session_data["client_public_key"].encode('utf-8')
            )
            server_public_key = serialization.load_pem_public_key(
                session_data["server_public_key"].encode('utf-8')
            )
            aes_key = bytes.fromhex(session_data["aes_key"])

            return {
                "host": session_data["host"],
                "port": session_data["port"],
                "server_mac_address": session_data["server_mac_address"],
                "client_public_key": client_public_key,
                "server_public_key": server_public_key,
                "aes_key": aes_key,
                "file_name": session_data["file_name"]
            }

        except Exception as e:
            print(f"[SessionManager.load_session] Błąd przy wczytywaniu sesji: {e}")
            return None
