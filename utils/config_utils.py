import __init__
from utils import read_from_yaml
from utils import constants as c

def get_config():
    return read_from_yaml.read_from_yaml(c.root_path + c.conf_path)


def get_host_from_config():
    return get_config()['general']['host']


def get_debug_flag_from_config():
    return get_config()['general']['debug']
