# the goal of this file is to launch everything.
# root path: os.path.dirname(os.path.abspath(__file__))
import os
from utils.read_from_yaml import read_from_yaml
from utils import general_utils as g

root_path = os.path.dirname(os.path.abspath(__file__))
conf_path = 'resources/fuse.yaml'
config = read_from_yaml(conf_path)

print(type(config['FUSE']['ACTIVATE_VENV']))

# activate_venv_windows = root_path + "\\flask\\flaskEnvironment\\Scripts\\activate"
# cmd = "deactivate"
#
# returned_value = os.system(cmd)  # returns the exit code in unix
# print('returned value:', returned_value)
#
print(os.path.dirname(os.path.abspath(__file__)))


def get_free_port():
    port_start_ind = config['FUSE']['FIRST_PORT']
    port_end_ind = config['FUSE']['LAST_PORT']
    busy_ports_json_path = config['GENERAL']['BUSY_PORTS_JSON_FILE']
    busy_ports_json = g.read_from_json(busy_ports_json_path)

    for i in range(port_start_ind, port_end_ind + 1):
        str_port = str(i)
        if not (str_port in busy_ports_json['busy_ports']):
            busy_ports_json['busy_ports'].append(str_port)
            g.write_to_json(busy_ports_json_path, busy_ports_json)
            return str_port





