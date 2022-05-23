# the goal of this file is to launch everything.
# root path: os.path.dirname(os.path.abspath(__file__))
import os
from utils.read_from_yaml import read_from_yaml
from utils import general_utils as g, db_utils

root_path = g.root_path
conf_path = g.conf_path
config = g.config

# test change
def start_venv():
    activate_venv_windows = root_path + config['fuse']['venv_activate_path']
    returned_value = os.system(activate_venv_windows)  # returns the exit code in unix
    g.print_c(f'venv activation code: {returned_value}')


def deact_venv():
    cmd = 'deactivate'
    returned_value = os.system(cmd)  # returns the exit code in unix
    g.print_c(f'venv deactivation code: {returned_value}')


def get_free_port():
    port_start_ind = config['fuse']['first_port']
    port_end_ind = config['fuse']['last_port']
    busy_ports_json = g.read_from_json(g.busy_ports_json_path)

    for i in range(port_start_ind, port_end_ind + 1):
        str_port = str(i)
        if not (str_port in busy_ports_json['busy_ports']):
            return str_port


def start_service(service_full_name, port, service_short_name, local=False, host=g.host):
    local_process = g.custom_subprocess.CustomNamedProcess([g.sys.executable,
                                                            service_full_name,
                                                            "-local", str(local),
                                                            "-port", str(port)],
                                                           name=service_short_name)
    g.launched_subprocesses.append(
        g.custom_subprocess.CustomProcessListElement(service_full_name,
                                                     port,
                                                     service_short_name,
                                                     local_process.pid,
                                                     local_process))
    g.print_c(f"fuse added service to pool: {service_full_name}")
    return local_process


def init_start_service_procedure(service, sys=False):
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

    if spawn_type != "multi":
        if local:
            new_process = start_service(service_full_name, port, service_short_name=service, local=local)
        else:
            new_process = start_service(service_full_name, port, service_short_name=service)
    else:
        raise Exception('Implement multi endpoint stuff')
    if sys:
        db_utils.insert_into_sys_services( service_full_name, port, new_process.pid)
    else:
        db_utils.insert_into_business_services(service_full_name, port, new_process.pid)


def main():
    g.print_c(f'Firing fuse..')
    # some preconfiguration
    g.clear_busy_ports()
    # TODO> I think remake busy ports into DB table. or?..
    db_utils.initial_table_creation()
    db_utils.clear_system_tables()
    db_utils.clear_business_tables()
    if config['fuse']['activate_venv']:
        g.print_c(f"starting venv from {root_path + config['fuse']['fuse']}")
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

