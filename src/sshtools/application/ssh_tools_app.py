from argparse import ArgumentError, ArgumentTypeError
from os import path
from tqdm import tqdm
import cmd2
import pathlib
from cmd2.table_creator import BorderedTable,Column
from cmd2.ansi import style,strip_style
from time import time
from sshtools.services import SSHService
from sshtools.configuration import config
from sshtools.models import SessionInfo
from sshtools.utils import ValidateFileAction,read_file,Password
from sshtools.utils.connetion_info import ConnectionInfo

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
    ssh_parser.add_argument('-i','--info',required=False,type=ConnectionInfo,help="specify connection info")
    ssh_parser.add_argument('-p','--port',required=False,help="specify port")
    ssh_parser.add_argument('-cm','-dcommand',default=None,help="specify the default command")
    @cmd2.with_argparser(ssh_parser)
    def do_add(self, args):
        """starts an ssh service"""
        if args.file is None and args.info is None:
            self.ssh_parser.print_usage()
            self.print(style("Error: one of the following arguments is required: file, info",fg="red"))
            return
        if args.file is not None and args.info is not None:
            self.ssh_parser.print_usage()
            self.print(style("Error: only one of those argument can be provided: file, info",fg="red"))
            return
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
                if args.port:
                    args.info.port = args.port
                session_info = SessionInfo(args.info.ip,args.info.port,args.info.username,args.info.password.value,args.dcommand)
                self.ssh_service.add(session_info)
                if args.connect:
                        self.ssh_service.connect(f"{session_info.server_ip}:{session_info.server_port}")
            except Exception as err:
                pass

    ssh_connect_parser = cmd2.Cmd2ArgumentParser()
    ssh_connect_parser.add_argument('-l','--list',nargs='+',help='list of sessions to connect.')
    @cmd2.with_argparser(ssh_connect_parser)
    def do_connect(self,args):
        '''connects to the ssh sessions in the service'''
        if args.list is None or len(args.list):
            to_connect = [key for key,sess in self.ssh_service.sessions.items() if not sess.is_connected()]
        else:
            to_connect = [key for key,sess in self.ssh_service.sessions.items() if not sess.is_connected() and key in args.list]
        if not len(to_connect):
            self.print(style("no sessions to connect.",fg='yellow'))
            return
        with tqdm(total=100) as pbar:
            pbar.set_lock(self.ssh_service.lock)
            start = time()
            results = self.ssh_service.connect(args.list,callback=pbar.update)
            end = time()
        table_data = [[row.session_id,style(row.status,fg='green') if row.status == 'success' else style(row.status,fg='red'),row.message,row.connection_time]for row in results]
        self.__set_table_width(self.conn_table,table_data)
        self.print(self.conn_table.generate_table(table_data))
        self.print(f"time: {end - start}")

    ssh_disconnect_parser = cmd2.Cmd2ArgumentParser()
    ssh_disconnect_parser.add_argument('-l','--list',nargs='+',help='list of sessions to disconnect from.')
    @cmd2.with_argparser(ssh_disconnect_parser)
    def do_disconnect(self,args):
        '''disconnects the ssh sessions in the service'''
        results = self.ssh_service.disconnect(args.list)
        table_data = [[res.session_id,style(res.status,fg='bright_black'),res.message,res.connection_time] for res in results]
        self.__set_table_width(self.conn_table,table_data)
        self.print(self.conn_table.generate_table(table_data))     
    
    ssh_exec_parser = cmd2.Cmd2ArgumentParser()
    ssh_exec_parser.add_argument('-cm','--command',default=None,required=False,help="specify command to execute")
    ssh_exec_parser.add_argument('-l','--list',nargs='+',help='list of sessions to execute on.')
    @cmd2.with_argparser(ssh_exec_parser)
    def do_exec(self,args):
        '''execute command on the ssh sessions'''
        if args.list is None or not len(args.list):
            execut_on = [key for key,sess in self.ssh_service.sessions.items() if sess.is_connected()]
        else:
            execut_on = [key for key,sess in self.ssh_service.sessions.items() if sess.is_connected() and key in args.list]
        if not len(execut_on):
            self.print(style("no sessions to execute on. consider adding or connecting sessions.",fg='yellow'))
            return
        with tqdm(total=100) as pbar:
            pbar.set_lock(self.ssh_service.lock)
            start = time()
            results = self.ssh_service.exec_command(args.command,execut_on,callback=pbar.update)
            end = time()
        table_data = [[result.session_id,style('failed',fg='red') if result.stderr_text else style('success',fg='green'),result.stderr_text if result.stderr_text else result.stdout_text,result.execution_time] for result in results]
        self.__set_table_width(self.result_table,table_data)
        self.print(self.result_table.generate_table(table_data))
        self.print(f"time: {end - start}")

    ssh_remove_parser = cmd2.Cmd2ArgumentParser()
    ssh_remove_parser.add_argument('-l','--list',nargs='+',help='list of sessions to remove.')
    @cmd2.with_argparser(ssh_remove_parser)
    def do_remove(self,args):
        '''removes the ssh session(s) from the service'''      
        results = self.ssh_service.remove(args.list)
        if not len(results):
            self.print(style("didn't find any session to remove.",fg='yellow'))
            return
        conn_data = [[row.session_id,style(row.status,fg='green') if row.status == 'success' else style(row.status,fg='red') if row.status == 'failure' else style(row.status,fg='bright_black'),row.message,row.connection_time]for row in results]
        title = f"Removed {len(results)} sessions:"
        self.print(style(title,fg="cyan"))
        self.print('='*len(title))
        self.__set_table_width(self.conn_table,conn_data)
        self.print(self.conn_table.generate_table(conn_data))
    
    ssh_show_parser = cmd2.Cmd2ArgumentParser()
    ssh_show_parser.add_argument('-c','--connections',nargs='*',help='id of the session to show the connection data of.')
    ssh_show_parser.add_argument('-s','--sessions',nargs='*',help='id of the sessions to show.')
    ssh_show_parser.add_argument('-e','--executions',type=int,nargs='*',help='id of the exec to show.')
    @cmd2.with_argparser(ssh_show_parser)
    def do_show(self,args):
        self.ssh_service.update_status()

        if args.executions is None and args.connections is None and args.sessions is None:
            self.ssh_show_parser.print_usage()
            self.print(style("Error: one of the following arguments is required: connections, sessions or executions",fg="red"))
            return

        if args.executions is not None:
            ids = set([ex.exec_id for ex in self.ssh_service.exec_results])
            if not len(ids):
                self.print(style("no executions to show.",fg='yellow'))
            if not len(args.executions):
                args.executions = ids  
            for exe_id in args.executions:
                if exe_id in ids:
                    title = f"Execution: #{exe_id}"
                    self.print(style(title,fg="cyan"))
                    self.print('='*len(title))
                    exec_to_show = [res for res in self.ssh_service.exec_results if res.exec_id == exe_id]
                    exec_data = [[result.session_id,style('failed',fg='red') if result.stderr_text else style('success',fg='green'),result.stderr_text if result.stderr_text else result.stdout_text,result.execution_time] for result in exec_to_show]
                    self.__set_table_width(self.result_table,exec_data)
                    self.print(self.result_table.generate_table(exec_data))
        
        if args.connections is not None:
            if len(args.connections):
                conn_to_show =  [con for key,con in self.ssh_service.conn_results.items() if key in args.connections]
            else:
                conn_to_show = self.ssh_service.conn_results.values()
            if not len(conn_to_show):
                self.print(style("no connections to show.",fg='yellow'))
                return
            conn_data = [[row.session_id,style(row.status,fg='green') if row.status == 'success' else style(row.status,fg='red') if row.status == 'failure' else style(row.status,fg='bright_black'),row.message,row.connection_time]for row in conn_to_show]
            self.__set_table_width(self.conn_table,conn_data)
            self.print(self.conn_table.generate_table(conn_data))
        
        if args.sessions is not None:
            if len(args.sessions):
                sessions_to_show =  [ses for key,ses in self.ssh_service.sessions.items() if key in args.sessions]
            else:
                sessions_to_show = self.ssh_service.sessions.values()
            if not len(sessions_to_show):
                self.print(style("no sessions to show.",fg='yellow'))
                return
            for session in sessions_to_show:
                title = f"Session: {session.id}"
                self.print(style(title,fg="cyan"))
                self.print('='*len(title))
                if session.id not in self.ssh_service.conn_results.keys():
                    conn_data = [[session.id,style('disconnected',fg='bright_black'),'session has never been connected.','none']]
                else:
                    res = self.ssh_service.conn_results[session.id]
                    conn_data = [[res.session_id,style(res.status,fg='green') if res.status == 'success' else style(res.status,fg='red') if res.status == 'failure' else style(res.status,fg='bright_black'),res.message,res.connection_time]]
                    self.__set_table_width(self.conn_table,conn_data)
                    self.print(self.conn_table.generate_table(conn_data))

                execotions = [exe for exe in self.ssh_service.exec_results if exe.session_id == session.id]
                if execotions:
                    exec_data = [[result.session_id,style('failed',fg='red') if result.stderr_text else style('success',fg='green'),result.stderr_text if result.stderr_text else result.stdout_text,result.execution_time] for result in execotions]
                    self.__set_table_width(self.result_table,exec_data)
                    self.print(self.result_table.generate_table(exec_data))
        

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

    def __set_table_width(self,table:BorderedTable,input_rows):
        for col in table.cols:
            l = len(strip_style(col.header))
            col.width = l if l > 0 else 1
        for input in input_rows:
            for i in range(len(input)):
                l = len(strip_style(input[i]))
                if l > table.cols[i].width:
                    if l > 50:
                        table.cols[i].width = 50
                    else:
                        table.cols[i].width = l

