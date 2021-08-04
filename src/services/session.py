from cmd2.ansi import style
from paramiko import  SSHClient,AutoAddPolicy
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
from models import CommandResult
from utils import ConnectionError

class Session:
    use_sys_host_key = False
    auto_add_policy = False
    def __init__(self,app,ip:str,port:int,user:str,password:str=None) -> None:
        self.ssh_client = SSHClient()
        self.app = app
        if self.use_sys_host_key:
            self.ssh_client.load_system_host_keys()
        if self.auto_add_policy:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            self.ssh_client.connect(hostname=ip,port=port,username=user,password=password)
        except BadHostKeyException:
            raise ConnectionError(message="Invalid host key.")
        except AuthenticationException:
            raise ConnectionError(message="Authentication failed, Check your username and password.")
        except SSHException as err:
            raise ConnectionError(message=f"Failed to connect to the server at {ip}:{port}.")
        except Exception as err:
             raise ConnectionError(message=f"Failed to connect to the server at {ip}:{port}.")

    def __del__(self):
        self.ssh_client.close()
        self.app.print(style('Session closed'))

    def exec_command(self,command:str):
        try:
            stdin,stdout,stderr = self.ssh_client.exec_command(command)
            inp = command
            oup = stdout.read().decode()
            err = stderr.read().decode()
            return CommandResult(inp,oup,err)
        except Exception as err:
            inp = command
            oup= "none"
            err = err
            return CommandResult(inp,oup,err)