import __init__
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

import schedule
import time
import utils.general_utils as g

from utils import constants as c
from utils import yaml_utils

import requests
from utils import logger_utils as log

from utils import db_utils

# DO NOT IMPORT. (this file) !@!!!!!!

root_path = c.root_path

SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name
log.get_log(c.life_ping_schedule_name)


def ping_one(port):
    try:
        r = requests.patch(f"http://localhost:{port}{c.life_ping_endpoint_context}").status_code
        if r:
            return 'alive'
    except Exception as e:
        log.info(e)
        return 'dead'


def process_one_service(n):
    try:
        config = yaml_utils.get_config()
        if n['status'] == 'dead':
            g.get_rid_of_service_by_pid(n['pid'])

            if config['services']['system'].get(n['name'], None) is not None:
                g.init_start_service_procedure(n['name'], is_sys=True)
                return
            if config['services']['business'].get(n['name'], None) is not None:
                g.init_start_service_procedure(n['name'], is_sys=False)
                return
            log.error(f"Tried to revive '{n['name']}' but it was not found in config services lists")

    except Exception as e:
        log.error(
            f"Failed to properly process service {n['name']}, pid {n['pid']}, port {n['port']}, status {n['status']}")
        log.error(e)


def process_service_statuses(services_and_statuses):
    with ThreadPoolExecutor(max_workers=len(services_and_statuses)) as executor:
        for result in executor.map(process_one_service, services_and_statuses):
            pass


def ping_services(services, services_and_statuses):
    with ThreadPoolExecutor(max_workers=len(services)) as executor:
        for result in executor.map(ping_one_service_and_more, services, repeat(services_and_statuses)):
            pass


def job():
    log.info("Scheduled life_ping task started..")
    try:
        services = db_utils.select_from_table(SYS_SERVICES_TABLE_NAME) + db_utils.select_from_table(
            BUSINESS_SERVICES_TABLE_NAME)
        services_and_statuses = []

        ping_services(services, services_and_statuses)
        process_service_statuses(services_and_statuses)
    except Exception as e:
        log.exception(f"Main life ping schedule body exceptioned")
        log.exception(e)
    log.info("Scheduled life_ping task finished")


def ping_one_service_and_more(service, services_and_statuses):
    try:
        service_status = ping_one(service.port)
        services_and_statuses.append(
            {'name': service.name, 'port': service.port, 'pid': service.pid, 'status': service_status})
        if service['status'] != service_status:
            db_utils.change_service_status_by_pid(service.pid, service_status)
        short_name = service['name'].split('\\')[-1]
        log.debug(f"Endpoint {short_name} (localhost:{service.port}) is {service_status}")
    except Exception as e:
        log.exception(f"Something went wrong while pinging in lifping scheduler")
        log.exception(e)


schedule.every(15).seconds.do(job)
# schedule.every(1).minute.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except:
    log.error(f"{c.life_ping_schedule_name} loop exited")
