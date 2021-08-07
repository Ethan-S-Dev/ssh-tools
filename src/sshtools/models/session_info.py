class SessionInfo:
    def __init__(self,ip:str,port:int,username,password:str=None,default_command:str=None) -> None:
        # TODO: Add Validation!
        self.server_ip = ip
        self.server_port = port
        self.username = username
        self.password = password
        self.default_command = default_command