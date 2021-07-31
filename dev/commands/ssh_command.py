from dev.exceptions import FileError
from typing import Callable
import magic
import os.path as path
from dev import read_json,read_excel,read_csv

mimes:dict[str,Callable[[str],list]] = {
    "application/json":read_json,
    "text/csv":read_csv,
    "application/vnd.ms-excel":read_excel,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":read_excel
}

def connections_from_file(file_path:str):
    if path.exists(file_path):
        file_mime = magic.from_file(file_path,mime=True)
        if file_mime not in mimes:
            raise FileError(f"The file: '{file_path}' is not supported.")
        conn_list = mimes[file_mime](file_path)


argv:dict[str,Callable] = {
    "-f":connections_from_file
}

def ssh_command(args:list[str]):
    if len(args) == 0:
        raise Exception
    
    if args[0] in argv:
        if len(args) < 2:
            raise Exception
        argv[args[0]](args[1])
        

                

