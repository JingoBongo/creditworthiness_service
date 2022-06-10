import subprocess
import sys
from utils import logger_utils


class CustomNamedProcess(subprocess.Popen):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        # todo, mess w/ folder for logs
        # self.log = logger_utils.setup_logger(name, )
        super().__init__(*args, **kwargs)


class CustomProcessListElement():
    def __init__(self, full_name, port, short_name, pid, obj_reference):
        self.full_name = full_name
        self.port = port
        self.short_name = short_name
        self.pid = pid
        self.obj_reference = obj_reference

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
