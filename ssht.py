from dev import get_command,CommandError,config,help
import sys
from rich import print
        
def main(args):
    try:
        config()
        if len(args) <= 1:
            help()
            return
        argc = args[1]
        if(len(args) == 2):
            get_command(argc)
            return
        argv = args[2:]
        get_command(argc)(*argv)
    except CommandError as err:
        print(err)
    except Exception as wtf:
        print(wtf)

if __name__ == "__main__":
    main(sys.argv)