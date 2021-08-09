from getpass import getpass

from sshtools.utils.password import Password
class ConnectionInfo:
    DEFAULT = 'user@ip'

    def __init__(self, value:str):
        if not value:
            raise ValueError()
        values = value.split('@')
        if len(values) != 2:
            raise ValueError()
        self.username = values[0]
        self.ip = values[1]
        self.port = 22
        self.password = Password('')