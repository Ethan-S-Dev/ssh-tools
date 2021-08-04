from services import Session
from cmd2.ansi import style
import json
from os import path
from .this_path import config_path

def config(app):    
    if path.exists(config_path):
        conf = open(config_path)
        data = json.load(conf)
        if data["UseSysHostKey"]:
            Session.use_sys_host_key = True
        if data["AutoAddPolicy"]:
            Session.auto_add_policy = True
    else:
        app.print(style("Cant find config file.",fg='red'))
            