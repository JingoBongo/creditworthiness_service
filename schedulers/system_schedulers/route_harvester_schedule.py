import __init__
import schedule
import time
import utils.general_utils as g
from utils import constants as c
import os
import requests
from utils import logger_utils as log

from utils import db_utils

# DO NOT IMPORT. (his file) !@!!!!!!

root_path = c.root_path
config = g.config

SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name
cur_file_name = os.path.basename(__file__)
log.get_log(c.route_harvester_schedule_name)



def job():
    log.info("Scheduled route_harvester task started..")
    # what exactly do we expect to harvest here?
    # we probably only run through alive services. k.
    services = g.db_utils.select_from_table(SYS_SERVICES_TABLE_NAME) + g.db_utils.select_from_table(
        BUSINESS_SERVICES_TABLE_NAME)
    # so we still get services from tables.
    # we need to update corresponding table tho.
    # so, table 'harvested route' with columns
    # service_name, function name, harvested route
    # TODO, how to handle <string:etc> in harvested routes? for now try to just coyp paste
    # TODO, harvesting can result in multiple routes for one function, therefore store function name
    # TODO, actually, I don't want to clean harvested routes. let them be updated only by timer or by error
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
                    # lets try it like this. collect route as long as func is not met
                    # if there are >0 routes, add them
                    if line.startswith('@') and '.route(' in line:
                        try:
                            temp_routes.append(line.split("'")[1])
                        except:
                            print(f"while getting temp route, double quotes found and managed")
                            temp_routes.append(line.split('"')[1])
                    if line.startswith('def'):
                    #  we caught all routes for func, add to all routes
                        function = line.split(' ')[1].split('(')[0]
                        for route in temp_routes:
                            try:
                                all_routes.append({'service_name':service_name, 'function_name':function, 'route':route})
                            except:
                                log.exception(f"Tried to add {route} to all routes, it seems to be a ???")
                                log.exception(f"All routes until that exception: {all_routes}")
                        temp_routes = []
                print() # after all lines`
        except Exception as e:
            log.exception(f"What went wrong during processing {service['name']}?")
            log.exception(e)

        print() # after file close
    print()  # to check all routes
    # insert harvested routes into db
    # TODO, I need to check for non existent routes here.
    # TODO finish/do logic about deleting non existent routes and adding only those that are new

    for route in all_routes:
        db_utils.insert_into_table(c.harvested_routes_table_name, route)
    print() # check db with routes.


schedule.every(15).seconds.do(job)
# schedule.every(10).minutes.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except:
    log.error(f"{c.route_harvester_schedule_name} loop exited")
