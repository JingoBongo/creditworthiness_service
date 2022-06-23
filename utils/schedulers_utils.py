import re

import __init__
from utils import general_utils as g, db_utils
from utils.subprocess_utils import start_generic_subprocess
from utils import constants as c
from utils import logger_utils as log

SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name

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

def route_is_in_routes(route, routs_from_db):
#     route and function_name, service_name, route
    for rroute in routs_from_db:
        if route['route'] == rroute['route'] and route['service_name'] == rroute['service_name'] and route['function_name'] == rroute['function_name']:
            return True
#           here we purely assume that duplicates do not exist in harvested route table
    return False


def route_harvester_job_body():
    log.info("Scheduled route_harvester task started..")
    # what exactly do we expect to harvest here?
    # we probably only run through alive services. k.
    services = g.db_utils.select_from_table(SYS_SERVICES_TABLE_NAME) + g.db_utils.select_from_table(
        BUSINESS_SERVICES_TABLE_NAME)
    # so we still get services from tables.
    # we need to update corresponding table tho.
    # so, table 'harvested route' with columns
    # service_name, function name, harvested route
    # for service_name, service_path from services work with file
    all_routes = []
    for service in services:
        try:
            service_path = service['path']
            service_name = service['name']
            log.info(f"Harvesting {service_name} - {service_path}")
            with open(service_path) as py_file:
                lines = py_file.readlines()
                temp_routes = []
                for line in lines:
                    if line.startswith('@') and '.route(' in line:
                        try:
                            t_route = line.split("'")[1][1:]
                        except:
                            print(f"while getting temp route, double quotes were found and managed")
                            t_route = line.split('"')[1][1:]

                        t_route = re.sub(r'<.+>', '<*>', t_route)
                        temp_routes.append(t_route)
                    if line.startswith('def'):
                        #  we caught all routes for func, add to all routes
                        function = line.split(' ')[1].split('(')[0]
                        for route in temp_routes:
                            try:
                                all_routes.append(
                                    {'service_name': service_name, 'function_name': function, 'route': route})
                            except:
                                log.exception(f"Tried to add {route} to all routes, it seems to be a ???")
                                log.exception(f"All routes until that exception: {all_routes}")
                        temp_routes = []
        except Exception as e:
            log.exception(f"What went wrong during processing {service['name']}?")
            log.exception(e)

    # insert harvested routes into db
    # 1. if route is in db but is not in all_routes, delete it
    harvested_routes_from_db = db_utils.select_from_table(c.harvested_routes_table_name)
    for route in harvested_routes_from_db:
        try:
            # if not route in routs_from_all_routes:
            if not route_is_in_routes(route, all_routes):
                # delete rows with such routes from db
                db_utils.delete_route_from_harvested_routes_by_route(route['route'])
        except Exception as e:
            log.exception(f"Something went wrong while processing route(from db) {route}")
            log.exception(e)
    # 2. if route is in all_routes but not in db, add it (instead of add all below)
    for route in all_routes:
        try:
            if not route_is_in_routes(route, harvested_routes_from_db):
                # add to db
                db_utils.insert_into_table(c.harvested_routes_table_name, route)
        except Exception as e:
            log.exception(f"Something went wrong while processing route(from pyfiles) {route}")
            log.exception(e)
    log.info(f"Route Harvester finished job")
