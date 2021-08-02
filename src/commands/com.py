from entities import console
from .ssh_command import SSHCommand
from util import CommandError

def ssh_command(*args):
    SSHCommand().start(list(args))

def help(command:str=None):
    if not command:
        with open("etc/help.txt") as helpText:
            console.print(helpText.read())
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