from commands import get_command
from util import CommandError
from configuration import config
from entities import console
import sys
    
def main(args):
    try:
        config()
        if len(args) <= 1:
            get_command("help")()
            return
        argc = args[1]
        if(len(args) == 2):
            get_command(argc)()
            return
        argv = args[2:]
        get_command(argc)(*argv)
    except CommandError as err:
        console.print(err)
    except Exception as wtf:
        console.print(wtf)

if __name__ == "__main__":
    main(sys.argv)