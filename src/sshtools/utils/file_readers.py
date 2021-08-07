import argparse
from typing import Union,Callable
import mimetypes
import os
import os.path as path
import pandas as pd


def read_excel(file_path:str,sheet_name:Union[int,str]=0)->list:
    df = pd.read_excel(file_path,sheet_name)
    return [v for v in df.to_dict('index').values()]

def read_csv(file_path:str)->list:
    df = pd.read_csv(file_path,skipinitialspace=True)
    return [v for v in df.to_dict('index').values()]

def read_json(file_path:str)->list:
    df = pd.read_json(file_path)
    return [v for v in df.to_dict('index').values()]


mimes:dict[str,Callable[[str],list]] = {
    "application/json":read_json,
    "text/csv":read_csv,
    "application/vnd.ms-excel":read_csv,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":read_excel
    }

def read_file(file_path:str):
    if not path.exists(file_path):
        file_path = path.join(os.getcwd(),file_path)
    exist = path.exists(file_path)
    if exist:
            file_mime = mimetypes.guess_type(file_path,True)[0]
            conn_list = mimes[file_mime](file_path)
            values_list = [[value for value in item.values()] for item in conn_list]
            return values_list

class ValidateFileAction(argparse.Action):
    mimes:list[str] = [
    "application/json",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, values)
            return
        path = str(values)
        file_mime = mimetypes.guess_type(path,True)[0]
        if file_mime not in self.mimes:
            raise ValueError("file must be csv, xl or json file.")
        setattr(namespace, self.dest, values)