import json
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import uuid


def get_public_key(key):
    public_key_pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_pem


def get_mac_address():
    mac = uuid.getnode()
    mac_address = ":".join(
        [f"{(mac >> i) & 0xff:02x}" for i in range(0, 8 * 6, 8)][::-1]
    )
    return mac_address


class SessionManager:

    @staticmethod
    def save_session(
        host,
        port,
        client_public_key,
        server_public_key,
        aes_key,
        file_name,
        client_mac_address,
    ):
        session_data = {
            "host": host,
            "port": port,
            "client_mac_address": client_mac_address,
            "client_public_key": client_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode(
                "utf-8"
            ),  # Serializacja do formatu PEM
            "server_public_key": server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8"),
            "aes_key": aes_key.hex(),  # Klucz AES zapisany w formie hex
            "file_name": file_name,
        }

        # Zapis do pliku JSON
        session_file_path = "session.json"
        try:
            with open(session_file_path, "w") as session_file:
                json.dump(session_data, session_file, indent=4)
            print("Session saved successfully.")
        except Exception as e:
            print(f"[SessionManager.save_session] Błąd przy zapisie sesji: {e}")

    def save_session_server(
        host,
        port,
        client_public_key,
        server_public_key,
        aes_key,
        file_name,
        server_mac_address,
    ):
        session_data = {
            "host": host,
            "port": port,
            "server_mac_address": server_mac_address,
            "client_public_key": client_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode(
                "utf-8"
            ),  # Serializacja do formatu PEM
            "server_public_key": server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8"),
            "aes_key": aes_key.hex(),  # Klucz AES zapisany w formie hex
            "file_name": file_name,
        }

        # Zapis do pliku JSON
        session_file_path = "session_server.json"
        try:
            with open(session_file_path, "w") as session_file:
                json.dump(session_data, session_file, indent=4)
            print("Session saved successfully.")
        except Exception as e:
            print(f"[SessionManager.save_session] Błąd przy zapisie sesji: {e}")

    @staticmethod
    def load_session():
        session_file_path = "session.json"

        if not os.path.exists(session_file_path):
            print("[SessionManager.load_session] Brak pliku z zapisaną sesją.")
            return None

        try:
            with open(session_file_path, "r") as session_file:
                session_data = json.load(session_file)

            # Przywracanie danych sesji z pliku
            client_public_key = serialization.load_pem_public_key(
                session_data["client_public_key"].encode("utf-8")
            )
            server_public_key = serialization.load_pem_public_key(
                session_data["server_public_key"].encode("utf-8")
            )
            aes_key = bytes.fromhex(session_data["aes_key"])

            return {
                "host": session_data["host"],
                "port": session_data["port"],
                "client_mac_address": session_data["client_mac_address"],
                "client_public_key": client_public_key,
                "server_public_key": server_public_key,
                "aes_key": aes_key,
                "file_name": session_data["file_name"],
            }

        except Exception as e:
            print(
                f"[SessionManager.load_session] Błąd przy wczytywaniu sesji: {e}"
            )
            return None

    @staticmethod
    def load_session_server():
        session_file_path = "session_server.json"

        if not os.path.exists(session_file_path):
            print("[SessionManager.load_session] Brak pliku z zapisaną sesją.")
            return None

        try:
            with open(session_file_path, "r") as session_file:
                session_data = json.load(session_file)

            # Przywracanie danych sesji z pliku
            client_public_key = serialization.load_pem_public_key(
                session_data["client_public_key"].encode("utf-8")
            )
            server_public_key = serialization.load_pem_public_key(
                session_data["server_public_key"].encode("utf-8")
            )
            aes_key = bytes.fromhex(session_data["aes_key"])

            return {
                "host": session_data["host"],
                "port": session_data["port"],
                "server_mac_address": session_data["server_mac_address"],
                "client_public_key": client_public_key,
                "server_public_key": server_public_key,
                "aes_key": aes_key,
                "file_name": session_data["file_name"],
            }

        except Exception as e:
            print(
                f"[SessionManager.load_session] Błąd przy wczytywaniu sesji: {e}"
            )
            return None
