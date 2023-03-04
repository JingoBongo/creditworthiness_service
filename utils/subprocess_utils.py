import __init__
import sys

from utils.dataclasses.custom_named_subprocess import CustomNamedSubprocess


# TODO: move those in dataclasses?




def start_generic_subprocess(name, path):
    # A note to keep in mind: sys.executable is python, therefore this is for
    # launching python file code
    local_process = CustomNamedSubprocess([sys.executable, path], name=name)
    return local_process


def start_service_subprocess(service_full_path, local_part, port_part, name_part, service_short_name):
    # A note to keep in mind: sys.executable is python, therefore this is for
    # launching python file code THAT IS A SERVICE
    port1 = port_part[0]
    port2 = port_part[1]
    local1 = local_part[0]
    local2 = local_part[1]
    name1 = name_part[0]
    name2 = name_part[1]
    local_process = CustomNamedSubprocess([sys.executable, service_full_path, local1, local2, port1, port2, name1, name2],
                                          name=service_short_name)
    return local_process
