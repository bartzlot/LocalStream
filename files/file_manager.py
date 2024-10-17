
class FileManager:
    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                print(f"File '{file_path}' successfully loaded.")
                return file_data       
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
        return None
