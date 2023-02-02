import __init__

from utils import logger_utils as log
import platform
import psutil


def is_linux_running():
    return platform.system() == "Linux"

def get_memory_percent_load():
    return psutil.virtual_memory().percent

def get_free_memory_percend_load():
    return psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

def get_cpu_percent_load():
    return psutil.cpu_percent(interval=1, percpu=True)

def get_cpu_load_avg():
    load = get_cpu_percent_load()
    return sum(load) / len(load)
