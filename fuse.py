import sys

import __init__
from utils import logger_utils as log
from utils.package_utils import run_importing_process
run_importing_process()
import os


from utils import general_utils as g
from utils import db_utils
from utils import constants as c

root_path = c.root_path
conf_path = c.conf_path
config = g.config
# cur_file_name = os.path.basename(__file__)


def setup_cur_logger():
    log.get_log('fuse')
    # c.current_subprocess_logger = log
    # sys.excepthook = handle_exception

# def print_c(text):
#     # print(f"[{cur_file_name}] {str(text)}")
#     c.current_subprocess_logger.info(f"[{cur_file_name}] {str(text)}")

def try_service_launch(service_name: str, service_config: dict, is_system: bool):
    if service_config.get('enabled', None) == False:
        log.warn(f"Service '{service_name}' is disabled in config and therefore will not be launched")
        return
    if service_config.get('path', None) == None:
        log.error(f"Service '{service_name}' has no path specified in config and therefore will not be launched")
        return
    g.init_start_service_procedure(service_name, sys=is_system)

def main():
    g.recreate_log_foler_if_not_exists()
    setup_cur_logger()
    # print_c(f'Firing fuse..')
    log.info(f'Firing fuse..')
    print(c.fuse_logo)
    # some preconfiguration
    g.clear_busy_ports()
    g.generate_on_start_unique_fuse_id()
    # TODO THIS IS JUST FOR TESTING PURPOSES
    # in future, probably clear only after task is resolved in any way
    # TODO: thing is, on start it should try to relaunch stopped tasks ince, then clear the tasks file
    g.clear_tasks_file()
    g.clear_log_folder()
    g.reserve_ports_from_config()
    db_utils.initial_db_creation()
    db_utils.initial_table_creation()
    db_utils.clear_system_services_table()
    db_utils.clear_business_services_table()
    db_utils.clear_schedulers_table()
    db_utils.clear_table(c.all_processes_table_name)
    # TODO below is just for testing, as harvester this should just not be deleted
    # db_utils.clear_tasks_table()
    # fire system endpoints
    # Is all this checking necessary? I am not sure anymore

    system_services = config['services']['system']
    business_services = config['services']['business']

    if isinstance(system_services, dict) and isinstance(business_services, dict):
        if len(system_services) != 0:
            for service_name, service_config in zip(system_services.keys(), system_services.values()):
                try_service_launch(service_name, service_config, True)
        else:
            log.error('No system service found, not right at all')

        if len(business_services) != 0:
            for service_name, service_config in zip(business_services.keys(), business_services.values()):
                try_service_launch(service_name, service_config, False)
        else:
            log.error('No business service found, is it test launch?')
    while True:
        pass


if __name__ == "__main__":
    main()
