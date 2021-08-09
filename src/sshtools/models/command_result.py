from datetime import datetime
class CommandResult:
    def __init__(self,exec_id:int,session_id:str,stdin:str,stdout:str,stderr:str) -> None:
        self.execution_time = str(datetime.now())
        self.exec_id = exec_id
        self.session_id = session_id
        self.stdin_text = stdin
        self.stdout_text = stdout
        self.stderr_text = stderr
