from dev.ssh_sessions import Client, CommandResult, Session, SessionInfo
from dev.exceptions import CommandError, FileError
from typing import Callable, Tuple
import magic
import os.path as path
from dev.file_readers import read_json,read_excel,read_csv
from dev import console
from rich.table import Table

class SSHCommand():
    mimes:dict[str,Callable[[str],list]] = {
    "application/json":read_json,
    "text/csv":read_csv,
    "application/vnd.ms-excel":read_excel,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":read_excel
    }

    def __init__(self) -> None:
        self.argv:dict[str,Callable] = {
        "-f":self.__connections_from_file,
        "-c":self.__set_first_command
        }
        self.commands:dict[str,Tuple[Callable,int,int]] = {
            "add":(self.__add_connection,2,4),
            "exec":(self.__exec,0,2),
            "history":(self.__print_result,1,1)
        }
        self.next_id = 0
        self.client = Client([])
        self.exec_results = list[dict[int,CommandResult]]()
        self.first_command = None

    def __connections_from_file(self,file_path:str):
        if path.exists(file_path):
            file_mime = magic.from_file(file_path,mime=True)
            if file_mime not in SSHCommand.mimes:
                raise FileError(f"The file: '{file_path}' is not supported.")
            conn_list = SSHCommand.mimes[file_mime](file_path)
            self.client = Client([SessionInfo(*args) for args in conn_list])
            self.next_id = len(self.client.connections)
    
    def __set_first_command(self,command:str):
        self.first_command = command

    def __add_connection(self,ip_port:str,username:str,password:str=None,command:str=None):
        ip_port_list = ip_port.split(":")
        if len(ip_port_list) != 2:
            raise CommandError(f"Server connection: '{ip_port}' is invalid.")
        ip =ip_port_list[0]
        port = 0
        try:
            port = int(ip_port_list[1])
        except ValueError:
            raise CommandError(f"Server connection: '{ip_port}' is invalid.")
        return SessionInfo(ip,port,username,password,command)

    def __exec(self,command:str=None,*session_ids):
        return self.client.exec_command(command,list(session_ids))

    def __get_result_table(self,index:int):
        table = Table(f"Result for execution #{index}")

        table.add_column("Server",style="cyan")
        table.add_column("Input")
        table.add_column("Output")
        table.add_column("Error")

        for key,result in self.exec_results[index-1].items():
            conn_info = self.client.connections[key]
            table.add_row(f"{conn_info.server_ip}:{conn_info.server_port}",f"{result.stdin_text}",f"{result.stdout_text}",f"[red/]{result.stderr_text}[/]")
        return table

    def start(self,args:list[str]):
        if len(args) > 0:
            if len(args)%2 != 0:
                    raise CommandError("Invalid command args.")        
            for index in range(0,len(args),2):
                if args[index] in self.argv:
                    raise CommandError(f"Invalid command '{args[index]}'.")
                self.argv[args[index]](args[index+1])

        if self.first_command is not None:
            try:
                self.client.exec_command(self.first_command)
            except CommandError as err: 
                console.print(err.message)

        self.__loop()
        
    def __loop(self):
        while True:
                try:
                    command = input("$> ")
                    if command.lower() == "exit":
                        break
                    command_list = command.split()
                    command = command_list[0]
                    command_args = command_list[1:]
                    if command not in self.commands:
                        raise CommandError(f"Invalid command: '{command_list[0]}', see 'help ssh' for more info.")
                    if len(command_args) < self.commands[command][1] or len(command_args) > self.commands[command][2]:
                        raise CommandError(f"Invalid command args: {command_args} - for command:'{command_list[0]}', see 'help ssh' for more info.")
                    result = self.commands[command][0](*command_args)
                    if isinstance(result,SessionInfo): 
                        self.client.connect(self.next_id,result)
                        self.next_id += 1
                        self.client.print_connections()
                        continue
                    if isinstance(result,dict[int,CommandResult]):
                        self.client.print_results()
                        self.exec_results.append(result)
                        continue
                    if isinstance(result,Table):
                        console.print(result)
                        continue
                    console.print("No result.")
                except KeyboardInterrupt:
                    break
                except CommandError as err:
                    console.print(err.message)

                

