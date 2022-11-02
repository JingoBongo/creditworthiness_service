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
from utils.schedulers_utils import route_harvester_job_body

root_path = c.root_path


SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name
cur_file_name = os.path.basename(__file__)
log.get_log(c.route_harvester_schedule_name)


def job():
    route_harvester_job_body()


# schedule.every(15).seconds.do(job)
schedule.every(2).minutes.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except:
    log.error(f"{c.route_harvester_schedule_name} loop exited")
