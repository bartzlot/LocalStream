class ErrorHandler: 

    @staticmethod
    def error_handling(method_name: str, error):
        print(f"[FileManager.{method_name}] An unexpected error occurred: [{error}]")
