import __init__
from utils import read_from_yaml
from utils import constants as c

def getConfig():
    return read_from_yaml.read_from_yaml(c.root_path + c.conf_path)


def getHostFromConfig():
    return getConfig()['general']['host']


def getDebugFlagFromConfig():
    return getConfig()['general']['debug']
