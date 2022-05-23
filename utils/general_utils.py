import json
import os
import utils.read_from_yaml as yaml_utils

SYS_SERVICES_TABLE_NAME = 'Sys_Services'
BUSINESS_SERVICES_TABLE_NAME = 'Business_Services'
LIFE_PING_ENDPOINT_CONTEXT = '/life_ping'
cur_file_name = os.path.basename(__file__)
root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
conf_path = '.\\resources\\fuse.yaml'
config = yaml_utils.read_from_yaml(conf_path)
busy_ports_json_path = root_path + config['general']['busy_ports_json_file']
debug = config['general']['debug']
host = config['general']['host']

# TODO remove this, as I see this value isn't passed between processes and endpoints, therefore useless
launched_subprocesses = []


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def run_cmd_command(command):
    print_c(f'triggering command :{command}')
    returned_value = os.system(command)
    print_c(f'returned value: {returned_value}')


def read_from_json(path):
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except Exception as e:
        print_c(f'Something went horribly wrong when attempted to read from file "{path}"')
        print_c(e)
        return {}


def write_to_json(path, text):
    try:
        with open(path, 'w') as outfile:
            json.dump(text, outfile)
    except Exception as e:
        print_c(f'Something went horribly wrong when attempted to write into file "{path}" this specific text "{text}"')
        print_c(e)


def clear_busy_ports():
    new_json = {"busy_ports": ['5000']}
    write_to_json(busy_ports_json_path, new_json)


def set_port_busy(port):
    busy_ports_json = read_from_json(busy_ports_json_path)
    busy_ports_json['busy_ports'].append(port)
    write_to_json(busy_ports_json_path, busy_ports_json)


def set_environment_variable(param, param1):
    os.environ[param] = str(param1)
