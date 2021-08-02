from os import path

this_grand_parent_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
etc_path = path.join(this_grand_parent_dir,"etc")
config_path = path.join(etc_path,"config.json")
help_path = path.join(etc_path,"help.txt")

