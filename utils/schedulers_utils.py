import __init__
from utils import general_utils as g
from utils.subprocess_utils import start_generic_subprocess
from utils import constants as c
from utils import logger_utils as log


def launch_scheduler_if_not_exists(process_name, process_full_path):
    table_results = g.db_utils.select_from_table('Schedulers')
    table_results_names = [x['name'] for x in table_results]
    if not process_name in table_results_names:
        local_process = start_generic_subprocess(process_name, process_full_path)
        g.db_utils.insert_into_schedulers(process_name, process_full_path, local_process.pid)
        log.info(f"Started '{process_name}' scheduler at pid '{local_process.pid}'")
    else:
        log.warn(f"While launching endpoint with scheduler an attempt to add duplicate '{process_name}' was refused")


def launch_life_ping_scheduler_if_not_exists():
    process_name = c.life_ping_schedule_name
    process_full_path = f"{c.root_path}//{c.schedulers_folder_name}//{c.system_schedulers_folder_name}//{c.life_ping_schedule_pyfile_name}"
    launch_scheduler_if_not_exists(process_name, process_full_path)



def launch_route_harvester_scheduler_if_not_exists():
    process_name = c.route_harvester_schedule_name
    process_full_path = f"{c.root_path}//{c.schedulers_folder_name}//{c.system_schedulers_folder_name}//{c.route_harvester_schedule_pyfile_name}"
    launch_scheduler_if_not_exists(process_name, process_full_path)