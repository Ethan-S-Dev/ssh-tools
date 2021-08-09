from datetime import datetime
class ConnectionResult:
    def __init__(self,session_id:str,status:str,message:str) -> None:
        self.session_id = session_id 
        self.status = status 
        self.message = message 
        self.connection_time = str(datetime.now())