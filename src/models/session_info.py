class SessionInfo:
    def __init__(self,ip:str,port:int,username,password:str=None,command:str=None) -> None:
        self.server_ip = ip
        self.server_port = port
        self.username = username
        self.password = password
        self.command = command