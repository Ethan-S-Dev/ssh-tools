from cmd2.ansi import style
from models import SessionInfo,CommandResult
from utils import ConnectionError
from .session import Session
from cmd2.table_creator import BorderedTable,Column

class SSHService:
    def __init__(self,connections:list[SessionInfo],app) -> None:
        self.connections = {i:connections[i] for i in range(len(connections))}
        self.sessions = dict[int,Session]()
        self.app = app
        self.connection_table = BorderedTable([Column("id"),Column(style("Server",fg="cyan")),Column("Status"),Column("Message")])
        self.connection_table_rows =[]
        self.results_table = BorderedTable([Column("id"),Column(style("Server",fg="cyan")),Column("Status"),Column("Message")])
        self.results_table_rows =[]
    
    def __del__(self):
        print = (len(self.sessions.values()) > 0)
        for key in self.sessions.keys():
            session = self.sessions.get(key)
            del session
        if print:
            self.app.print("Deleted all sessions.")

    def connect(self,session_id:int=None,session_info:SessionInfo=None):
        if session_id is None:
            self.connection_table_rows.clear()   
            for con_id,con_info in self.connections.items():
                try:
                    session = Session(self.app,con_info.server_ip,con_info.server_port,con_info.username,con_info.password)
                    self.sessions[con_id] = session
                    row_input = [str(con_id),f"{con_info.server_ip}:{con_info.server_port}",style("success",fg='green'),"Connected Successfully!"]
                    self._set_table_width(self.connection_table,row_input)
                    self.connection_table_rows.append(row_input)
                except ConnectionError as err:
                    row_input = [str(con_id),f"{con_info.server_ip}:{con_info.server_port}",style("failed",fg='red'),err.message]
                    self._set_table_width(self.connection_table,row_input)
                    self.connection_table_rows.append(row_input)
            return

        if session_info is None:
            session_info = self.connections[session_id]
        try:
            session = Session(self.app,session_info.server_ip,session_info.server_port,session_info.username,session_info.password)
            self.sessions[session_id] = session
            row_input = [str(session_id),f"{session_info.server_ip}:{session_info.server_port}",style("success",fg='green'),"Connected Successfully!"]
            self._set_table_width(self.connection_table,row_input)
            self.connection_table_rows.append(row_input)
        except ConnectionError as err:
            row_input = [str(session_id),f"{session_info.server_ip}:{session_info.server_port}",style("failed",fg='red'),err.message]
            self._set_table_width(self.connection_table,row_input)
            self.connection_table_rows.append(row_input)
    
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
           
    def exec_command(self,command:str=None,session_ids:list[int]=None):
        self.results_table_rows.clear()
        if session_ids is None or len(session_ids) == 0:
            session_ids = list(self.sessions.keys())
        if command is None:
            session_to_exec = {session_id:session for session_id,session in self.sessions.items() if session_id in session_ids and self.connections[session_id].command is not None}
            results = dict[int,CommandResult]()
            for session_id,session in session_to_exec.items():
                command = self.connections[session_id].command
                results[session_id] = session.exec_command(command)          
        else:
            session_to_exec = {session_id:session for session_id,session in self.sessions.items() if session_id in session_ids}
            results = dict[int,CommandResult]()
            for session_id,session in session_to_exec.items():
                results[session_ids] = session.exec_command(command)
        for id,result in results.items():
            session_info = self.connections.get(id)
            row_input = [str(id),f"{session_info.server_ip}:{session_info.server_port}",style("success",fg='green') if len(result.stderr_text) == 0 else style("failed",fc='red'),f"{result.stdout_text}" if len(result.stderr_text) == 0 else f"{result.stderr_text}"]
            self._set_table_width(self.results_table,row_input)
            self.results_table_rows.append(row_input)
        return results
    
    def print_connections(self):
        self.app.print(self.connection_table.generate_table(self.connection_table_rows))
    
    def print_results(self):
        self.app.print(self.results_table.generate_table(self.results_table_rows))

    def _set_table_width(self,table,input):
        for i in range(len(input)):
            if len(input[i]) > table.cols[i].width:
                if len(input[i]) > 50:
                    table.cols[i].width = 50
                else:
                    table.cols[i].width = len(input[i])