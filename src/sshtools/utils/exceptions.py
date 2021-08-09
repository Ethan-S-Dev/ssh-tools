class CommandError(Exception):
    def __init__(self,message:str,*args) -> None:
        self.message = message
        super().__init__(args)

class ConnectionError(Exception):
    def __init__(self,message:str,*args) -> None:
        self.message = message
        super().__init__(args)

class FileError(Exception):
    def __init__(self,message:str,*args) -> None:
        self.message = message
        super().__init__(args)