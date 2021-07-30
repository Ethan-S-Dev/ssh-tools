from .exceptions import CommandError
from rich import print

def ssh(ip:str,username:str,password:str,command:str):
    print(f'Connecting to {ip} with user: {username}\n\tExecuting command: "{command}".')

def help(command:str):
    if not command:
        print(open("../etc/help.txt"))
        return
    print(command)



commands_list = {
    "ssh":ssh,
    "help":help,
    "--help":help
}

def get_command(key:str):
    try:
        return commands_list[key.lower()]
    except KeyError:
        raise CommandError(f"Can't find command named: {key.lower()}, for list of use 'ssh-tool help'")