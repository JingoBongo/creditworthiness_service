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
log.get_log(c.taskmaster_schedule_name)
# c.current_subprocess_logger = log


def process_new_task(task):
#     now we need to find if this fuse supports needed task
    directory_to_iterate = c.root_path + config['general']['tasks_folder']
    supported_tasks = []
    for filename in os.listdir(directory_to_iterate):
        f = os.path.join(directory_to_iterate, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)


def process_task_in_progress(task):
    log.error(f"Implement me: process_task_in_progress!!!!")


def treat_task_according_to_status(task):
    if task['status'] == c.tasks_status_new:
        process_new_task(task)
    elif task['status'] == c.tasks_status_in_progress:
        process_task_in_progress(task)
    else:
        log.info(f"Task {task['task_name']} was ignored by taskmaster scheduler since it was not 'new' or 'in progress'")


def job():
    log.info(f"Scheduled {c.taskmaster_schedule_name} task started..")
#     so, we have a file of tasks to check
    tasks = g.read_from_tasks_json_file()['tasks']
#   in theory, we only care about tasks that are new? what to do with in progress frozen/errored?
#   let errored stay errored with some data
#   let frozen.. hm. I need to check if there is a pool working on the task. if not, work with in progress too
    for task in tasks:
        try:
            treat_task_according_to_status(task)
        except Exception as e:
            log.exception(f"Something went horribly wrong while trying to process task {task['task_name']}")
            log.exception(e)

schedule.every(15).seconds.do(job)
# schedule.every(1).minute.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except:
    log.error(f"{c.taskmaster_schedule_name} loop exited")
