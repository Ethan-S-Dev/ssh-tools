from models import Session
from common import console
import json
from os import path
from common import config_path

def config():    
    if path.exists(config_path):
        conf = open(config_path)
        data = json.load(conf)
        if data["UseSysHostKey"]:
            Session.use_sys_host_key = True
        if data["AutoAddPolicy"]:
            Session.auto_add_policy = True
    else:
        console.print("[red]Cant find config file.[/]")
            