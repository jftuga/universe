
from enum import Enum

# SAVE:: command output is save to a file
device_commands = {}
device_commands["hp_procurve"]    = ( "no page", "SAVE::show run" )
device_commands["hp_comware"]     = ( "SAVE::display current-configuration", )
device_commands["paloalto_panos"] = ( "set cli pager off", "SAVE::show config running")
device_commands["ubiquiti_edge"]  = ( "configure", "run terminal length 9999", "SAVE::run show configuration all", "exit")

class re_filter_type(Enum):
    include = 1
    exclude = 2

re_device_includes = {}
re_device_includes["hp_procurve"] = "[0-9a-f]{6}-[0-9a-f]{6}", "Up", "Down"

re_device_excludes = {}
re_device_excludes["hp_procurve"] = "^$", "Running configuration", "^;"



