# the goal of this file is to launch everything.
# root path: os.path.dirname(os.path.abspath(__file__))
import os


from utils.named_custom_process import CustomNamedProcess, CustomProcessListElement
from utils.read_from_yaml import read_from_yaml
from utils import general_utils as g
from utils import db_utils

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
                try:
                    enabled = config['services']['business'][service]['enabled']
                except:
                    enabled = True
                if enabled:
                    g.init_start_service_procedure(service, sys=True)
    # fire user endpoints
    if isinstance(config['services']['business'], dict):
        if len(config['services']['business']) > 0:
            for service in config['services']['business']:
                try:
                    enabled = config['services']['business'][service]['enabled']
                except:
                    enabled = True
                if enabled:
                    g.init_start_service_procedure(service)


if __name__ == "__main__":
    # g.run_cmd_command('cd')
    main()
    #     just an eternal loop
    while True:
        pass
