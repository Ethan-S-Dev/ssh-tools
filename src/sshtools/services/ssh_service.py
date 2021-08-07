from typing import Callable, Union
from cmd2.ansi import style
from models import SessionInfo,CommandResult,ConnectionResult
from utils import ConnectionError,ConnectionResult
from .session import Session
from concurrent.futures import ThreadPoolExecutor

class SSHService:
    def __init__(self) -> None:
        self.sessions = dict[str,Session]()
        self.conn_results = list[ConnectionResult]()
        self.exec_results = list[CommandResult]()
        #self.connection_table = BorderedTable([Column("id"),Column(style("Server",fg="cyan")),Column("Status"),Column("Message")])
        #self.results_table = BorderedTable([Column("id"),Column(style("Server",fg="cyan")),Column("Status"),Column("Message")])
    
    def load_sys_host_key(self):
        for session in self.sessions.values():
            session.load_sys_host_key()
    
    def use_auto_add_policy(self):
        for session in self.sessions.values():
            session.use_auto_add_policy()

    def add(self,session_info:SessionInfo):
        id = f"{session_info.server_ip}:{session_info.server_port}"
        self.sessions[id] = Session(session_info)

    def connect(self,session_id:Union[str,list[str]]=None,callback:Callable=None):
        if session_id is None:
            sessions_to_connect = [(s,callback) for s in self.sessions.values() if not s.is_connected]
            with ThreadPoolExecutor() as executer:
                results = executer.map(self.__connect,sessions_to_connect)
                self.conn_results.append(results)
        if isinstance()

    def __connect(self,session:Session,callback:Callable=None):
        result = session.connect()
        if callback:
            callback()
        return result

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

#    def _set_table_width(self,table,input):
#       for i in range(len(input)):
#            if len(input[i]) > table.cols[i].width:
#                if len(input[i]) > 50:
#                    table.cols[i].width = 50
#                else:
#                    table.cols[i].width = len(input[i])

    def __del__(self):
        print = (len(self.sessions.values()) > 0)
        for key in self.sessions.keys():
            session = self.sessions.get(key)
            del session
        if print:
            self.app.print("Deleted all sessions.")