import subprocess
import sys


class CustomNamedProcess(subprocess.Popen):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)



def start_generic_subprocess(name, path):
    local_process = CustomNamedProcess([sys.executable, path], name=name)
    return local_process


def start_service_subprocess(service_full_path, local_part, port_part, service_short_name):
    port1 = port_part[0]
    port2 = port_part[1]
    local1 = local_part[0]
    local2 = local_part[1]
    local_process = CustomNamedProcess([sys.executable, service_full_path, local1, local2, port1, port2], name=service_short_name)
    return local_process
