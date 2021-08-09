from getpass import getpass
class Password:
    DEFAULT = 'Prompt if not specified'

    def __init__(self, value):
        if not value:
            value = getpass('Session Password: ')
        self.value = value

    def __str__(self):
        return self.value