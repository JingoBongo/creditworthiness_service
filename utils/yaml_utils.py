import __init__
import yaml

from utils import constants as c
from utils import logger_utils as log


def read_from_yaml(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        log.exception(e)
        log.exception(f"*not a proper print* error reading {file_path} file")


def get_config():
    return read_from_yaml(c.root_path + c.conf_path)


def get_host_from_config():
    return get_config()['general']['host']


def get_debug_flag_from_config():
    return get_config()['general']['debug']
