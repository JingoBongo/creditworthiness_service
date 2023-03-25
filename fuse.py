import __init__
from utils.package_utils import run_importing_process

run_importing_process()
import os
import signal
import threading

from utils import logger_utils as log, os_utils
from utils import yaml_utils
from utils import general_utils as g
from utils import db_utils
from utils import constants as c


def setup_cur_logger():
    log.get_log('fuse')


def try_service_launch(service_name: str, service_config: dict, is_system: bool):
    """
    try launching service considering its dict config structure

    Args:
        service_name (str): name of the service that will be checked
        service_config (dict): configuration of the service to be launched
        is_system (bool): is service system one, or business one
    """
    if not service_config.get('enabled', True):
        log.warn(f"Service '{service_name}' is disabled in config and therefore will not be launched")
        return
    if service_config.get('path', None) is None:
        log.error(f"Service '{service_name}' has no path specified in config and therefore will not be launched")
        return
    g.init_start_service_procedure(service_name, is_sys=is_system)


def signal_handler(signum, frame):
    """
    Signal handler that terminates all subprocesses and threads.
    """
    os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
    threading.Timer(5, os.kill, args=(os.getpid(), signal.SIGKILL)).start()


def main():
    # some preconfiguration & init activities
    g.recreate_log_folder_if_not_exists()
    g.recreate_temporary_files_folder_if_not_exists()
    setup_cur_logger()
    log.info(f'Firing fuse..')
    print(c.fuse_logo)
    db_utils.initial_db_creation()
    db_utils.initial_table_creation()
    g.clear_busy_ports()
    g.generate_on_start_unique_fuse_id()
    g.clear_log_folder()
    # g.clear_temporary_files_folder()
    g.reserve_ports_from_config()
    db_utils.clear_system_services_table()
    db_utils.clear_business_services_table()
    db_utils.clear_schedulers_table()
    db_utils.clear_table(c.all_processes_table_name)
    config = yaml_utils.get_config()
    log.warn(f"[!!!] Going with config : {c.root_path + c.conf_path}")
    if os_utils.is_linux_running():
        log.warn(f"[!!!] On linux machine it is needed to sudo chmod 755 ./fuse.py (once)")
    signal.signal(signal.SIGINT, signal_handler)
    system_services = config['services']['system']
    business_services = config['services']['business']

    #   in both of the cases below, check given services list to be a dict and launch
    # them depending on their role
    if isinstance(system_services, dict):
        if len(system_services) != 0:
            for service_name, service_config in zip(system_services.keys(), system_services.values()):
                try_service_launch(service_name, service_config, True)
        else:
            log.error('No system service found, not right at all')

    if isinstance(business_services, dict):
        if len(business_services) != 0:
            for service_name, service_config in zip(business_services.keys(), business_services.values()):
                try_service_launch(service_name, service_config, False)
        else:
            log.error('No business service found, is it test launch?')
    log.info(f'Kaboom. Welcome.')

    #   the while that survived
    while True:
        pass


if __name__ == "__main__":
    main()
