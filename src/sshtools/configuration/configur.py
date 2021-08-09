from cmd2.ansi import style
import json
from os import path

def config(app):
    this_grand_parent_dir = app.app_path
    etc_path = path.join(this_grand_parent_dir,"etc")
    config_path = path.join(etc_path,"config.json")
    help_path = path.join(etc_path,"help.txt")    
    if path.exists(config_path):
        conf = open(config_path)
        data = json.load(conf)
        if data["UseSysHostKey"]:
            app.use_sys_host_key = True
        if data["AutoAddPolicy"]:
            app.auto_add_policy = True
    else:
        app.print(style("Cant find config file.",fg='red'))


