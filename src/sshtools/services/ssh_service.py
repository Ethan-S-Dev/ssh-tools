import threading
from typing import Callable
from cmd2.ansi import style
from sshtools.models import SessionInfo,CommandResult,ConnectionResult,Policy, policy
from .session import Session
from concurrent.futures import ThreadPoolExecutor

class SSHService:
    def __init__(self) -> None:
        self.sessions = dict[str,Session]()
        self.conn_results = dict[str,ConnectionResult]()
        self.exec_results = list[CommandResult]()
        self.lock = threading.Lock()
        self.execution_id = 1
        self.host_key_policy = Policy.Reject
        self.auto_load_sys_host_key = False
        #self.connection_table = 
        #self.results_table = BorderedTable([Column("id"),Column(style("Server",fg="cyan")),Column("Status"),Column("Message")])
    
    def load_sys_host_key(self,session_ids:list[str]=None,filename:str=None):
        if session_ids is None or not len(session_ids):
            for session in self.sessions.values():
                session.load_sys_host_key(filename)
        else:
            for session in [self.sessions[id] for id in session_ids]:
                session.load_sys_host_key()
    
    def use_auto_add_policy(self):
        self.host_key_policy = Policy.AutoAdd
        for session in self.sessions.values():
            session.use_auto_add_policy()

    def use_reject_policy(self):
        self.host_key_policy = Policy.Reject
        for session in self.sessions.values():
            session.use_reject_policy()

    def use_warning_policy(self):
        self.host_key_policy = Policy.Warning
        for session in self.sessions.values():
            session.use_warning_policy()

    def add(self,session_info:SessionInfo):
        id = f"{session_info.server_ip}:{session_info.server_port}"
        self.sessions[id] = Session(session_info)
        switch = {
          Policy.AutoAdd:self.sessions[id].use_auto_add_policy,
          Policy.Reject:self.sessions[id].use_reject_policy,
          Policy.Warning:self.sessions[id].use_warning_policy
        }
        switch[self.host_key_policy]()
        if self.auto_load_sys_host_key:
            self.sessions[id].load_sys_host_key()
    
    def remove(self,session_id:str):
        session = self.sessions.pop(session_id)
        if session and session.is_connected:
            session.disconnect()

    def connect(self,session_ids:list[str]=None,callback:Callable=None):
        if session_ids is None or not len(session_ids):
            sessions_to_connect = [s for s in self.sessions.values() if not s.is_connected]
        else:
            sessions_to_connect = [self.sessions[id] for id in session_ids]
        number_of_sessions = len(sessions_to_connect)
        sessions_args_list = ((s,number_of_sessions,callback) for s in sessions_to_connect)
        with ThreadPoolExecutor() as executer:
            results = list(executer.map(lambda p: self.__connect(*p),sessions_args_list))
        return results

    def __connect(self,session:Session,nsessions:int,callback:Callable=None):
        #print(f'conn {session.id}')
        result = session.connect()
        self.lock.acquire()
        self.conn_results[result.session_id] = result
        self.lock.release() 
        if callback:
            callback(100/nsessions)
        
        return result

    def disconnect(self,session_ids:list[str]=None):
        if session_ids is None or not len(session_ids):
            sessions_to_disconnect = self.sessions.values()
        else:
            sessions_to_disconnect = [self.sessions[id] for id in session_ids]
        for session in sessions_to_disconnect:
            session.disconnect()
            self.conn_results[session.id].status = style('disconnected',fg="lightgray")     
           
    def exec_command(self,command:str=None,session_ids:list[str]=None,callback:Callable=None):
        exec_id = self.execution_id
        self.execution_id += 1
        if session_ids is None or not len(session_ids):
            sessions_to_work = [s for s in self.sessions.values() if s.is_connected]
        else:
            sessions_to_work = [self.sessions[id] for id in session_ids if self.sessions[id] and self.sessions[id].is_connected]
        if command is None:
            sessions_to_exec = [[s,exec_id,s.default_command,callback] for s in sessions_to_work if s.default_command]
        else:
            sessions_to_exec = [[s,exec_id,command,callback] for s in sessions_to_work]
        nsessions = len(sessions_to_exec)
        execution_args_list = [[nsessions]+s for s in sessions_to_exec]
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda p: self.__exec_command(*p),execution_args_list))
            self.exec_results.extend(results)
        return results

    def set_banner_timeout(self,time:int):
        for session in self.sessions.values():
            session.banner_timout = time
    
    def __exec_command(self,nsessions:int,session:Session,execution_id:int,command:str,callback:Callable=None):
        result = session.exec_command(execution_id,command)
        if callback:
            callback(100/nsessions)
        return result
       
    def __del__(self):
        self.disconnect()

#    