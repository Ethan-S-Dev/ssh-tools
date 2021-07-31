from typing import Union
import pandas as pd

def read_excel(file_path:str,sheet_name:Union[int,str]=0)->list:
    df = pd.read_excel(file_path,sheet_name,skipinitialspace=True)
    return [v for v in df.to_dict('index').values()]

def read_csv(file_path:str)->list:
    df = pd.read_csv(file_path,skipinitialspace=True)
    return [v for v in df.to_dict('index').values()]

def read_json(file_path:str)->list:
    df = pd.read_json(file_path)
    return [v for v in df.to_dict('index').values()]
