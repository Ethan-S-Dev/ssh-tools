from paramiko import  SSHClient,AutoAddPolicy
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from models import CommandResult, ConnectionResult
from cmd2.ansi import style

from sshtools.models.session_info import SessionInfo

class Session:
    def __init__(self,session_info:SessionInfo) -> None:
        self.ssh_client = SSHClient()
        self.is_connected = False
        self.id = f"{session_info.server_ip}:{session_info.server_port}"
        self.ip = session_info.server_ip
        self.port = session_info.server_ip
        self.username = session_info.username
        self.password = session_info.password
        self.default_command = session_info.default_command

    def connect(self):      
        try:
            self.ssh_client.connect(hostname=self.ip,port=self.port,username=self.user,password=self.password)
            self.is_connected = True
            return ConnectionResult(self.id,status=style('success',fg='green'),message='Connected successfully to the server!')
        except BadHostKeyException:
            return ConnectionResult(self.id,status=style('failure',fg='red'),message='Invalid host key.')
        except AuthenticationException:
            return ConnectionResult(self.id,status=style('failure',fg='red'),message='Authentication failed, Check your username and password.')
        except SSHException as err:
            return ConnectionResult(self.id,status=style('failure',fg='red'),message=f'Failed to connect to the server at {self.ip}:{self.port}.')
        except Exception as err:
            return ConnectionResult(self.id,status=style('failure',fg='red'),message=f'Failed to connect to the server at {self.ip}:{self.port}.')
    
    def disconnect(self):
        if self.is_connected:
            self.ssh_client.close()
            self.is_connected = False

    def exec_command(self,exec_id:int,command:str):
        if self.is_connected:
            try:
                stdin,stdout,stderr = self.ssh_client.exec_command(command)
                inp = command
                oup = stdout.read().decode()
                err = stderr.read().decode()
                return CommandResult(exec_id,self.id,inp,oup,err)
            except Exception as err:
                inp = command
                oup= "none"
                err = err
                return CommandResult(exec_id,self.id,inp,oup,err)

    def load_sys_host_key(self):
        self.ssh_client.load_system_host_keys()
    
    def use_auto_add_policy(self):
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())

    def __del__(self):
        if self.is_connected:
            self.ssh_client.close()