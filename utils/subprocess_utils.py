import subprocess
import sys
from utils import logger_utils
from utils import constants as c


class CustomNamedProcess(subprocess.Popen):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        # logger_name = f"{name}-{self.pid}"
        # log_path = f"{c.root_path}resources//{c.logs_folder_name}//{logger_name}"
        # self.log = logger_utils.setup_logger(logger_name, log_path)
        super().__init__(*args, **kwargs)
        # todo, mess w/ folder for logs
        # self.log = logger_utils.setup_logger(name, )



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
