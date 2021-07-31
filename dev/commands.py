from dev import ssh_sessions
from dev.ssh_sessions import Client
from .exceptions import CommandError
from dev import ssh_command

def help(command:str=None):
    if not command:
        with open("etc/help.txt") as helpText:
            print(helpText.read())
        return
    print(command)

commands_list = {
    "ssh":ssh_command,
    "help":help
}

def get_command(key:str):
    try:
        return commands_list[key.lower()]
    except KeyError:
        raise CommandError(f"Can't find command named: {key.lower()}, for list of use 'help' command.")