from dev import ssh_client as client
from paramiko import AutoAddPolicy , 

import json
from os import path

def config():
    client.load_host_keys("../.ssh/known_hosts")
    if path.exists("etc/config.json"):
        conf = open("etc/config.json")
        data = json.load(conf)
        if data["AutoAddPolicy"]:
            client.set_missing_host_key_policy(AutoAddPolicy())