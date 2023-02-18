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


def save_config(contents):
    with open(c.root_path + c.conf_path, 'w') as outfile:
        yaml.dump(contents, outfile, default_flow_style=False)


def get_host_from_config():
    return get_config()['general']['host']


def get_secret_bin_path_from_config():
    config = get_config()
    string = config['fuse']['secret']['bin']
    if 'fuse_root + ' in string:
        return c.root_path + config['fuse']['secret']['bin'].replace('fuse_root + ', '')
    return config['fuse']['secret']['bin']


def get_secret_txt_path_from_config():
    config = get_config()
    string = config['fuse']['secret']['txt']
    if 'fuse_root + ' in string:
        return c.root_path + config['fuse']['secret']['txt'].replace('fuse_root + ', '')
    return config['fuse']['secret']['txt']


def get_debug_flag_from_config():
    return get_config()['general']['debug']


def get_cloud_repo_from_config():
    return get_config()['fuse']['cloud_repo']


def get_cloud_repo_username_from_config():
    return get_config()['fuse']['cloud_repo_username']





def set_service_enabled(service_name, boolean):
    config = get_config()
    for service in config['services']["system"]:
        if service == service_name:
            # if 'enabled' in service.keys():
            # if service.get('enabled', None):
            config['services']["system"][service]['enabled'] = boolean
            break
    for service in config['services']["business"]:
        if service == service_name:
            # if service.get('enabled', None):
            # if 'enabled' in service.keys():
            config['services']["business"][service]['enabled'] = boolean
        break
    save_config(config)
