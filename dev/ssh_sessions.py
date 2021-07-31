from colorama.initialise import init
from paramiko import SSHClient ,AutoAddPolicy
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from rich.table import Table
from .console import console
from .exceptions import ConnectionError

class CommandResult:
    def __init__(self,stdin:str,stdout:str,stderr:str) -> None:
        self.stdin_text = stdin
        self.stdout_text = stdin
        self.stderr_text = stdin

class SessionInfo:
    def __init__(self,ip:str,port:int,username,password:str=None) -> None:
        self.server_ip = ip
        self.server_port = port
        self.username = username
        self.password = password

class Session:
    use_sys_host_key = False
    auto_add_policy = False
    def __init__(self,ip:str,port:int,user:str,password:str=None) -> None:
        self.ssh_client = SSHClient()
        if self.use_sys_host_key:
            self.ssh_client.load_system_host_keys()
        if self.auto_add_policy:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.ssh_client.connect(ip,port,user,password)
        except BadHostKeyException:
            raise ConnectionError("Invalid host key.")
        except AuthenticationException:
            raise ConnectionError("Authentication failed, Check your username and password.")
        except SSHException as err:
            raise ConnectionError(f"Failed to connect to the server at {ip}:{port}.")

    def __del__(self):
        self.ssh_client.close()
        print("Session closed.")

    def exec_command(self,command:str):
        with self.ssh_client.exec_command(command) as std:
            return CommandResult(std[0].read(),std[1].read(),std[2].read())

class Client:
    def __init__(self,connections:list[SessionInfo]) -> None:
        self.connections = {i:connections[i] for i in range(len(connections))}
        self.sessions = dict[int,Session]()

        self.connection_table = Table("SHH Connections")
        self.connection_table.add_column("Server",style="cyan")
        self.connection_table.add_column("Status")
        self.connection_table.add_column("Message")

        self.results_table = Table("SHH Results")
        self.connection_table.add_column("Server",style="cyan")
        self.connection_table.add_column("Status")
        self.connection_table.add_column("Message")
    
    def __del__(self):
        for key in self.sessions.keys():
            session = self.sessions.pop(key)
            del session
        print("Deleted all sessions.")

    def connect(self,session_id:int=None,session_info:SessionInfo=None):
        if session_id is None:
            self.connection_table.rows.clear()   
            for con_id,con_info in self.connections.items():
                try:
                    session = Session(con_info.server_ip,con_info.server_port,con_info.username,con_info.password)
                    self.sessions[con_id] = session
                    self.connection_table.add_row(f"{con_info.server_ip}:{con_info.server_port}",f"[green]success[/]","Connected Successfully!")
                except ConnectionError as err:
                    self.connection_table.add_row(f"{con_info.server_ip}:{con_info.server_port}",f"[red]failed[/]",err.message)
            return

        if session_info is None:
            session_info = self.connections[session_id]
        try:
            session = Session(session_info.server_ip,session_info.server_port,session_info.username,session_info.password)
            self.sessions[session_id] = session
            self.connection_table.add_row(f"{session_info.server_ip}:{session_info.server_port}",f"[green]success[/]","Connected Successfully!")
        except ConnectionError as err:
            self.connection_table.add_row(f"{session_info.server_ip}:{session_info.server_port}",f"[red]failed[/]",err.message)
    
    def disconnect(self,session_id:int=None):
        if session_id is None:
            for session_id,session in self.sessions.items():
                session = self.connections.pop(session_id)
                del session
                self.connection_table.rows.pop(session_id)
            return
        if session_id in self.connections.keys():
            session = self.connections.pop(session_id)
            del session
            self.connection_table.rows.pop(session_id)
           
    def exec_command(self,command:str,session_ids:list[int]=None):
        self.results_table.rows.clear()
        if session_ids is None:
            session_ids = self.sessions.keys()
        
        results = {session_id:session.exec_command(command) for session_id,session in self.sessions.items() if session_id in session_ids}
        for id,result in results.items():
            session_info = self.connections.get(id) 
            self.results_table.add_row(f"{session_info.server_ip}:{session_info.server_port}","[green]Completed[/]" if len(result.stderr_text) == 0 else "[red]Error[/]",f"{result.stdout_text}" if len(result.stderr_text) == 0 else f"{result.stderr_text}")
            
    def print_connections(self):
        console.print(self.connection_table)
    
    def print_results(self):
        console.print(self.results_table)
                