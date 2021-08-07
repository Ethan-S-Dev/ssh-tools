class CommandResult:
    def __init__(self,exec_id:int,session_id:int,stdin:str,stdout:str,stderr:str) -> None:
        self.exec_id = exec_id
        self.session_id = session_id
        self.stdin_text = stdin
        self.stdout_text = stdout
        self.stderr_text = stderr