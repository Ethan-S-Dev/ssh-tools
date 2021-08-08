from os import path
from tqdm import tqdm
import cmd2
import pathlib
from cmd2.table_creator import BorderedTable,Column
from cmd2.ansi import style
from time import time
from sshtools.services import SSHService
from sshtools.configuration import config
from sshtools.models import SessionInfo
from sshtools.utils import ValidateFileAction,read_file,Password

class SSHToolsApp(cmd2.Cmd):
    
    def __init__(self):
        super().__init__(allow_cli_args=False)
        self.app_path = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))   
        self.ssh_service = SSHService()
        self.auto_load_sys_host_key = False
        self.host_key_policy = "reject"
        self.banner_timeout = 21
        self.add_settable(cmd2.Settable('banner_timeout', int, 'sets the banner timeout for the session connection', self,onchange_cb=self.__set_banner_timeout))
        self.add_settable(cmd2.Settable('auto_load_sys_host_key', bool, 'If True uses system host keys', self,onchange_cb=self.__set_auto_load_sys_host_key))
        self.add_settable(cmd2.Settable('host_key_policy', str, 'If True uses AutoAddPolicy for shh connections', self,choices=['reject','autoadd','warning'],onchange_cb=self.__set_host_key_policy))
        config(self)
        self.poutput(cmd2.style("- starting an ssh service -",fg='green',bold=True))
        self.prompt = "$> "
        self.conn_table = BorderedTable([Column(style("Target",fg="cyan")),Column("Status"),Column("Message"),Column('Time')])
        self.result_table = BorderedTable([Column(style("Target",fg="cyan")),Column("Status"),Column("Message"),Column('Time')])

    ssh_parser = cmd2.Cmd2ArgumentParser()
    ssh_parser.add_argument('-f','--file',default=None,type=pathlib.Path, action=ValidateFileAction, help='the file to load sessions from')
    ssh_parser.add_argument('-c','--connect',default=False,type=bool, help='if true auto connect session')
    ssh_parser.add_argument('-p','--ip',default=None,required=False,help="specify ip")
    ssh_parser.add_argument('-pt','--port',default=None,required=False,help="specify port")
    ssh_parser.add_argument('-u','--username',default=None,required=False,help="specify username")
    ssh_parser.add_argument('-ps','--password',default=None,required=False,type=Password,help="specify password")
    ssh_parser.add_argument('-dc','--dcommand',default=None,required=False,help="specify default command")

    @cmd2.with_argparser(ssh_parser)
    def do_add(self, args):
        """starts an ssh service""" 
        if args.file:
            conn_list = read_file(str(args.file))
            try:
                session_infos = [SessionInfo(*values) for values in conn_list]
                for session_info in session_infos:
                    self.ssh_service.add(session_info)
                    if args.connect:
                        self.ssh_service.connect(f"{session_info.server_ip}:{session_info.server_port}")
            except Exception as err:
                pass
        else:
            try:              
                session_info = SessionInfo(args.ip,args.port,args.username,args.password,args.dcommand)
                self.ssh_service.add(session_info)
                if args.connect:
                        self.ssh_service.connect(f"{session_info.server_ip}:{session_info.server_port}")
            except Exception as err:
                pass

    ssh_connect_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(ssh_connect_parser)
    def do_connect(self,args):
        '''connects to the ssh sessions in the service'''
        with tqdm(total=100) as pbar:
            pbar.set_lock(self.ssh_service.lock)
            start = time()
            results = self.ssh_service.connect(callback=pbar.update)
            end = time()
        table_data = [[result.session_id,result.status,result.message,str(result.connection_time)] for result in results]
        self.__set_table_width(self.conn_table,table_data)
        self.print(self.conn_table.generate_table(table_data))
        self.print(f"time: {end - start}")
    
    ssh_exec_parser = cmd2.Cmd2ArgumentParser()
    ssh_exec_parser.add_argument('-cm','--command',default=None,required=False,help="specify command to execute")

    @cmd2.with_argparser(ssh_exec_parser)
    def do_exec(self,args):
        '''execute command on the ssh sessions'''
        with tqdm(total=100) as pbar:
            pbar.set_lock(self.ssh_service.lock)
            start = time()
            results = self.ssh_service.exec_command(args.command,callback=pbar.update)
            end = time()
        table_data = [[result.session_id,style('failed',fg='red') if result.stderr_text else style('success',fg='green'),result.stderr_text if result.stderr_text else result.stdout_text,str(result.execution_time)] for result in results]
        self.__set_table_width(self.result_table,table_data)
        self.print(self.result_table.generate_table(table_data))
        self.print(f"time: {end - start}")

    def __set_auto_load_sys_host_key(self,name: str, before: bool, after: bool):
            if after:
                if self.ssh_service:
                    self.ssh_service.auto_load_sys_host_key = True
            else:
                if self.ssh_service:
                    self.ssh_service.auto_load_sys_host_key = False

    def __set_host_key_policy(self,name: str, before: str, after: str):
            if self.ssh_service:
                if after == 'autoadd':
                    self.ssh_service.use_auto_add_policy()
                    return
                if after == 'reject':
                    self.ssh_service.use_reject_policy()
                    return
                if after == 'warning':
                    self.ssh_service.use_warning_policy()
                    return

    def __set_banner_timeout(self,name: str, before: int, after: int):
            self.ssh_service.set_banner_timeout(after)
                
    def print(self,str:str):
        self.poutput(str)

    def __set_table_width(self,table,input_rows):
        for input in input_rows:
            for i in range(len(input)):
                if len(input[i]) > table.cols[i].width:
                    if len(input[i]) > 50:
                        table.cols[i].width = 50
                    else:
                        table.cols[i].width = len(input[i])

