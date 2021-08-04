import cmd2
import pathlib
from services import SSHService
from configuration import config
from models import SessionInfo
from utils import ValidateFileAction,read_file

class SSHToolsApp(cmd2.Cmd):
    
    def __init__(self):
        super().__init__()
        config(self)
        self.prompt = "$> "

    ssh_parser = cmd2.Cmd2ArgumentParser()
    ssh_parser.add_argument('-f','--file',default=None,type=pathlib.Path, action=ValidateFileAction, help='the file to load sessions from')

    @cmd2.with_argparser(ssh_parser)
    def do_ssh(self, args):
        """starts an ssh service"""        
        self.poutput(cmd2.style("- starting an ssh service -",fg='green',bold=True))
        if args.file:
            conn_list = read_file(str(args.file))
            self.service = SSHService([SessionInfo(*args) for args in conn_list],self)
        else:
            self.service = SSHService([],self)

    ssh_connect_parser = cmd2.Cmd2ArgumentParser()
   
    @cmd2.with_argparser(ssh_connect_parser)
    def do_connect(self,args):
        '''connects to the ssh sessions in the service'''
        self.service.connect()
        self.service.print_connections()
    
    ssh_exec_parser = cmd2.Cmd2ArgumentParser()

    @cmd2.with_argparser(ssh_exec_parser)
    def do_exec(self,args):
        '''execute command on the ssh sessions'''
        self.service.exec_command()
        self.service.print_results()
    
    def print(self,str:str):
        self.poutput(str)

app = SSHToolsApp()