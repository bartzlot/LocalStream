import os
import pathlib

class FileManager:

    @staticmethod
    def read_file(file_path: str, chunk_size: int, EOF_flag: bytes):

        try:
            with open(file_path, 'rb') as file:

                print(f"File '{file_path}' successfully loaded.")
                file_data = b""

                while True:

                    chunk = file.read(chunk_size)

                    if not chunk:
                        file_data += EOF_flag
                        break
                        
                    file_data += chunk

                file_name = os.path.basename(file_path)
                file_size = str(round(os.path.getsize(file_path) / 1024**2, 2))
                file_ext = pathlib.Path(file_path).suffix
                
                return [file_data, file_name, file_size, file_ext]
             
        except FileNotFoundError:
            print(f"[FileManager.read_file] Error: File '{file_path}' not found.")

        except IOError as e:
            print(f"[FileManager.read_file] I/O error occurred while reading the file: {e}")
            
        except Exception as e:
            print(f"[FileManager.read_file] An unexpected error occurred while reading the file: {e}")

        return None


    @staticmethod
    def save_file(file_path: str, file_bytes: bytes, EOF_flag: bytes):

        try:

            with open(file_path, "wb") as file:
                file.write(file_bytes.split(EOF_flag)[0])
            
        except FileNotFoundError:
            print(f"[FileManager.save_file] Error: File '{file_path}' not found.")

        except IOError as e:
            print(f"[FileManager.save_file] I/O error occurred while writing the file: {e}")
            
        except Exception as e:
            print(f"[FileManager.save_file] An unexpected error occurred while saving the file: {e}")

        return None