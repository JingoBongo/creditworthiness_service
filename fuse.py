# the goal of this file is to launch everything.
# root path: os.path.dirname(os.path.abspath(__file__))
import os
from utils.read_from_yaml import read_from_yaml
from utils import general_utils as g

root_path = os.path.dirname(os.path.abspath(__file__))
conf_path = 'fuse.yaml'
config = read_from_yaml(conf_path)

print(type(config['FUSE']['ACTIVATE_VENV']))


# activate_venv_windows = root_path + "\\flask\\flaskEnvironment\\Scripts\\activate"
# cmd = "deactivate"
#
# returned_value = os.system(cmd)  # returns the exit code in unix
# print('returned value:', returned_value)
#
print(os.path.dirname(os.path.abspath(__file__)))

def start_venv():
    activate_venv_windows = root_path + config['FUSE']['VENV_ACTIVATE_PATH']
    returned_value = os.system(activate_venv_windows)  # returns the exit code in unix
    g.printc(f'venv activation code: {returned_value}')


def deact_venv():
    cmd = 'deactivate'
    returned_value = os.system(cmd)  # returns the exit code in unix
    g.printc(f'venv deactivation code: {returned_value}')


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


def start_service(port, service_full_name, host='0.0.0.0'):
    start_service = f"set FLASK_APP={config['SERVICES']['BASE']['test1']} & flask run --host={host} -p {port}"
    # g.printc(f'triggering command :{start_service}')
    # returned_value = os.system(start_service)
    g.printc('is it working?')
    g.run_cmd_command(start_service)
    # g.printc(f'returned value: {returned_value}')





def main():
    g.printc(f'Firing fuse..')
    if config['FUSE']['ACTIVATE_VENV']:
        g.printc(f"starting venv from {root_path + config['FUSE']['VENV_ACTIVATE_PATH']}")
        start_venv()
    if config['FUSE']['START_TEST_SERVICES']:
        free_port = get_free_port()
        start_service(free_port, 'plchldr')


#         fire test services


if __name__ == "__main__":
    g.run_cmd_command('cd')
    main()
#     just an eternal loop
    while True:
        pass
