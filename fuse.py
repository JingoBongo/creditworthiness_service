import __init__
from utils.package_utils import run_importing_process
run_importing_process()
import os


from utils import general_utils as g
from utils import db_utils
from utils import constants as c
from utils import logger_utils

root_path = c.root_path
conf_path = c.conf_path
config = g.config
cur_file_name = os.path.basename(__file__)


def setup_cur_logger():
    log = logger_utils.get_log('fuse')
    c.current_subprocess_logger = log

def print_c(text):
    # print(f"[{cur_file_name}] {str(text)}")
    c.current_subprocess_logger.info(f"[{cur_file_name}] {str(text)}")



def main():
    setup_cur_logger()
    print_c(f'Firing fuse..')

    # some preconfiguration

    g.clear_busy_ports()
    g.clear_log_folder()
    g.reserve_ports_from_config()
    db_utils.initial_db_creation()
    db_utils.initial_table_creation()
    db_utils.clear_system_services_table()
    db_utils.clear_business_services_table()
    db_utils.clear_schedulers_table()
    # fire system endpoints
    # Is all this checking necessary? I am not sure anymore
    if isinstance(config['services']['system'], dict):
        if len(config['services']['system']) > 0:
            for service in config['services']['system']:
                if 'enabled' in config['services']['system'][service].keys():
                    if config['services']['system'][service]['enabled'] == False:
                        continue
                g.init_start_service_procedure(service, sys=True)
        else:
            print_c(f"It seems there are no system services to launch, it is not right")
    # fire business endpoints
    if isinstance(config['services']['business'], dict):
        if len(config['services']['business']) > 0:
            for service in config['services']['business']:
                if 'enabled' in config['services']['business'][service].keys():
                    if config['services']['business'][service]['enabled'] == False:
                        continue
                g.init_start_service_procedure(service)
        else:
            print_c(f"It seems there are no business services to launch, is it a test launch?")
    while True:
        pass


if __name__ == "__main__":
    main()
