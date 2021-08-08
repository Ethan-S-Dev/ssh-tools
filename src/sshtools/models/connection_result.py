from datetime import datetime
class ConnectionResult:
    def __init__(self,session_id:str,status:str,message:str) -> None:
        self.session_id = session_id #0
        self.status = status #0
        self.message = message #0
        self.connection_time = datetime.now() #0