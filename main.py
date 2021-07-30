from dev import getCommand,CommandError
import os
import sys
from os import path
from paramiko import SSHClient, AutoAddPolicy, client
from rich import print

client = SSHClient()
client.load_host_keys("~/.ssh/known_hosts")

def loadConfig():
    if path.exists("config.json"):
        print("config file exists!")


def main(argc:str,argv:list[str]):
    try:
        getCommand(argc)(*argv)
    except CommandError as err:
        print(err)

    


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2:])