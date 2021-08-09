from paramiko import  SSHClient,AutoAddPolicy,WarningPolicy
from paramiko.client import RejectPolicy, WarningPolicy
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from sshtools.models import CommandResult, ConnectionResult

from sshtools.models.session_info import SessionInfo

class Session:
    def __init__(self,session_info:SessionInfo) -> None:
        self.ssh_client = SSHClient()
        self.id = f"{session_info.server_ip}:{session_info.server_port}"
        self.ip = session_info.server_ip
        self.port = session_info.server_port
        self.username = session_info.username
        self.password = session_info.password
        self.default_command = session_info.default_command
        self.banner_timout = 10

    def connect(self):      
        try:
            if self.is_connected():
                return ConnectionResult(self.id,status='connected',message='Session all ready connected.')    
            self.ssh_client.connect(hostname=self.ip,port=self.port,username=self.username,password=self.password,banner_timeout=self.banner_timout)
            return ConnectionResult(self.id,status='success',message='Connected successfully to the server!')
        except BadHostKeyException:
            return ConnectionResult(self.id,status='failure',message='Invalid host key.')
        except AuthenticationException:
            return ConnectionResult(self.id,status='failure',message='Authentication failed, Check your username and password.')
        except SSHException as err:
            return ConnectionResult(self.id,status='failure',message=f'Failed to connect to the server at {self.ip}:{self.port}.\nException: {err}')
        except Exception as err:
            return ConnectionResult(self.id,status='failure',message=f'Failed to connect to the server at {self.ip}:{self.port}.\nException: {err}')
    
    def disconnect(self):
        if self.is_connected():
            self.ssh_client.close()

    def exec_command(self,exec_id:int,command:str):
        if self.is_connected():
            try:
                stdin,stdout,stderr = self.ssh_client.exec_command(command)
                inp = command
                oup = stdout.read().decode()
                err = stderr.read().decode()
                return CommandResult(exec_id,self.id,inp,oup,err)
            except Exception as err:
                return CommandResult(exec_id,self.id,command,"none",err)
        return CommandResult(exec_id,self.id,command,"none","Session is not connected.")

    def load_sys_host_key(self,filename:str=None):
        self.ssh_client.load_system_host_keys(filename)

    def load_host_key(self,filename:str):
        self.ssh_client.load_host_keys(filename)
    
    def use_auto_add_policy(self):
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())

    def use_warning_policy(self):
        self.ssh_client.set_missing_host_key_policy(WarningPolicy())

    def use_reject_policy(self):
        self.ssh_client.set_missing_host_key_policy(RejectPolicy())

    def is_connected(self):
        if self.ssh_client.get_transport():
            return self.ssh_client.get_transport().is_active()
        return False

    def __del__(self):
        if self.is_connected():
            self.ssh_client.close()
