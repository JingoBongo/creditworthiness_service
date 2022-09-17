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
    # TODO below is just for testing, as harvester this should just not be deleted
    # db_utils.clear_tasks_table()
    # fire system endpoints
    # Is all this checking necessary? I am not sure anymore
    # TODO: dima, do it in 1 loop.
    if isinstance(config['services']['system'], dict):
        if len(config['services']['system']) > 0:
            for service in config['services']['system']:
                if 'enabled' in config['services']['system'][service].keys():
                    if config['services']['system'][service]['enabled'] == False:
                        log.warn(f"Service '{service}' is disabled in config and therefore will not be launched")
                        continue
                if not 'path' in config['services']['system'][service].keys():
                    log.error(f"Service '{service}' has no path specified in config and therefore will not be launched")
                    continue
                g.init_start_service_procedure(service, sys=True)
        else:
            # print_c(f"It seems there are no system services to launch, it is not right")
            log.error(f"It seems there are no system services to launch, it is not right")
    # fire business endpoints
    if isinstance(config['services']['business'], dict):
        if len(config['services']['business']) > 0:
            for service in config['services']['business']:
                if 'enabled' in config['services']['business'][service].keys():
                    if config['services']['business'][service]['enabled'] == False:
                        log.warn(f"Service '{service}' is disabled in config and therefore will not be launched")
                        continue
                if not 'path' in config['services']['business'][service].keys():
                    log.error(f"Service '{service}' has no path specified in config and therefore will not be launched")
                    continue
                g.init_start_service_procedure(service)
        else:
            # print_c(f"It seems there are no business services to launch, is it a test launch?")
            log.warn(f"It seems there are no business services to launch, is it a test launch?")
    while True:
        pass


if __name__ == "__main__":
    main()
