import sys
from sshtools.application import SSHToolsApp

def main():
    app = SSHToolsApp()
    return sys.exit(app.cmdloop())

if __name__ == '__main__':
    main()
