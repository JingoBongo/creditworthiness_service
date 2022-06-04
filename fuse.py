import os

from utils.package_utils import run_importing_process
from utils import general_utils as g
from utils import db_utils

root_path = g.root_path
conf_path = g.conf_path
config = g.config
cur_file_name = os.path.basename(__file__)


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def main():
    print_c(f'Firing fuse..')
    run_importing_process()
    # some preconfiguration
    g.clear_busy_ports()
    # TODO> I think remake busy ports into DB table. or?..
    db_utils.initial_table_creation()
    db_utils.clear_system_tables()
    db_utils.clear_business_tables()
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
    while True:
        pass


if __name__ == "__main__":
    main()
