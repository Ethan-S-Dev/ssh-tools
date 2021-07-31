from ssh_sessions import Session
from paramiko import AutoAddPolicy

import json
from os import path

def config():
    if path.exists("etc/config.json"):
        conf = open("etc/config.json")
        data = json.load(conf)
        if data["UseSysHostKey"]:
            Session.use_sys_host_key = True
        if data["AutoAddPolicy"]:
            Session.auto_add_policy = True

            