class CommandResult:
    def __init__(self,stdin:str,stdout:str,stderr:str) -> None:
        self.stdin_text = stdin
        self.stdout_text = stdout
        self.stderr_text = stderr