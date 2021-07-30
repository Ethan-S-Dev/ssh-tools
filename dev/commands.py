from exceptions import CommandError

def ssh(ip:str,username:str,password:str,command:str):
    print(f'Connecting to {ip} with user: {username}\n\tExecuting command: "{command}".')

def help(command:str):
    if not command:
        print(
        '''usage: git
        


        ''')


commands = {
    "ssh":ssh,
    "help":help
}

def getCommand(key:str):
    try:
        return commands[key.lower()]
    except KeyError:
        raise CommandError(f"Can't find command named: {key.lower()}, for list of use 'ssh-tool help'")