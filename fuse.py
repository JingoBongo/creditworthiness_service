# the goal of this file is to launch everything.
# root path: os.path.dirname(os.path.abspath(__file__))
import os
from utils.read_from_yaml import read_from_yaml
from utils import general_utils as g

root_path = g.root_path
conf_path = g.conf_path
config = g.config

# print(type(config['fuse']['activate_venv']))
# print(os.path.dirname(os.path.abspath(__file__)))


# activate_venv_windows = root_path + "\\flask\\flaskEnvironment\\Scripts\\activate"
# cmd = "deactivate"
#
# returned_value = os.system(cmd)  # returns the exit code in unix
# print('returned value:', returned_value)
#

def start_venv():
    activate_venv_windows = root_path + config['fuse']['venv_activate_path']
    returned_value = os.system(activate_venv_windows)  # returns the exit code in unix
    g.printc(f'venv activation code: {returned_value}')


def deact_venv():
    cmd = 'deactivate'
    returned_value = os.system(cmd)  # returns the exit code in unix
    g.printc(f'venv deactivation code: {returned_value}')


def get_free_port():
    port_start_ind = config['fuse']['first_port']
    port_end_ind = config['fuse']['last_port']
    busy_ports_json = g.read_from_json(g.busy_ports_json_path)

    for i in range(port_start_ind, port_end_ind + 1):
        str_port = str(i)
        if not (str_port in busy_ports_json['busy_ports']):
            # busy_ports_json['busy_ports'].append(str_port)
            # g.write_to_json(busy_ports_json_path, busy_ports_json)
            return str_port


def start_service(service_full_name, port, local=False, host=g.host):
    # start_service = f"set FLASK_APP={config['services']['user']['endpoint_template']} & flask run --host={host} -p {port}"
    # # g.printc(f'triggering command :{start_service}')
    # # returned_value = os.system(start_service)
    # g.printc('is it working?')
    # g.run_cmd_command(start_service)
    # # g.printc(f'returned value: {returned_value}'
    local_process = g.subprocess.Popen([g.sys.executable, service_full_name, "-local", str(local), "-port", str(port)])
    g.launched_subprocesses.append(local_process)





def init_start_service_procedure(service, sys=False):
    br =6
    type = 'business'
    if sys:
        type = 'system'
    port = get_free_port()
    g.set_port_busy(port)
    service_full_name = root_path + config['services'][type][service]['path']
    try:
        local = config['services'][type][service]['local']
    except:
        local = None
    try:
        spawn_type = config['services'][type][service]['mono']
    except:
        spawn_type = None

    # os.environ["DEBUSSY"] = "1"
    g.set_environment_variable("FLASK_APP", "service_full_name")
    if spawn_type != "multi":
        if local:
            start_service(service_full_name, port, local)
        else:
            start_service(service_full_name,port)
    else:
        raise Exception('Implement multi endpoint stuff')




def main():
    g.printc(f'Firing fuse..')
    # some preconfiguration
    g.clear_busy_ports()
    if config['fuse']['activate_venv']:
        g.printc(f"starting venv from {root_path + config['fuse']['fuse']}")
        start_venv()
    # fire system endpoints
    if isinstance(config['services']['system'], dict):
        if len(config['services']['system']) > 0:
            for service in config['services']['system']:
                init_start_service_procedure(service, sys=True)
    # fire user endpoints
    if isinstance(config['services']['business'], dict):
        if len(config['services']['business']) > 0:
            for service in config['services']['business']:
                init_start_service_procedure(service)




if __name__ == "__main__":
    # g.run_cmd_command('cd')
    main()
#     just an eternal loop
    while True:
        pass
