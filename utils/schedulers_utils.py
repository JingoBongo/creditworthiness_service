import os
import re

import __init__
from utils import general_utils as g, db_utils
from utils.subprocess_utils import start_generic_subprocess
from utils import constants as c
from utils import logger_utils as log

SYS_SERVICES_TABLE_NAME = c.sys_services_table_name
BUSINESS_SERVICES_TABLE_NAME = c.business_services_table_name
config = g.config


def launch_scheduler_if_not_exists(process_name, process_full_path):
    table_results = g.db_utils.select_from_table('Schedulers')
    table_results_names = [x['name'] for x in table_results]
    if not process_name in table_results_names:
        local_process = start_generic_subprocess(process_name, process_full_path)
        g.db_utils.insert_into_schedulers(process_name, process_full_path, local_process.pid)
        log.info(f"Started '{process_name}' scheduler at pid '{local_process.pid}'")
    else:
        log.warn(f"While launching endpoint with scheduler an attempt to add duplicate '{process_name}' was refused")


def launch_taskmaster_scheduler_if_not_exists():
    process_name = c.taskmaster_schedule_name
    process_full_path = f"{c.root_path}//{c.schedulers_folder_name}//{c.system_schedulers_folder_name}//{c.taskmaster_schedule_pyfile_name}"
    launch_scheduler_if_not_exists(process_name, process_full_path)


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
        if route['route'] == rroute['route'] and route['service_name'] == rroute['service_name'] and route[
            'function_name'] == rroute['function_name']:
            return True
    #           here we purely assume that duplicates do not exist in harvested route table
    return False

def task_is_in_tasks(task, tasks_from_db):
    #     route and function_name, service_name, route
    for ttask in tasks_from_db:
        if task['task_full_path'] == ttask['task_full_path'] and task['task_name'] == ttask['task_name']:
            return True
    #           here we purely assume that duplicates do not exist in harvested route table
    return False


def process_new_task(task, task_file_content):
    #     now we need to find if this fuse supports needed task
    # change status of task with unique name to in progress
    old_val_tasks = g.read_from_tasks_json_file()
    for t in old_val_tasks['tasks']:
        if task['task_name'] == t['task_name']:
            t['status'] = c.tasks_status_in_progress
            break
    g.write_tasks_to_json_file(old_val_tasks)
    # start making tasks in a pool?


def process_task_in_progress(task, task_file_content):
    log.error(f"Implement me: process_task_in_progress!!!!")


def treat_task_according_to_status(task, task_file_content):
    if task['status'] == c.tasks_status_new:
        process_new_task(task, task_file_content)
    elif task['status'] == c.tasks_status_in_progress:
        process_task_in_progress(task, task_file_content)
    else:
        log.info(
            f"Task {task['task_name']} was ignored by taskmaster scheduler since it was not 'new' or 'in progress'")


def taskmaster_job_body():
    log.info(f"Scheduled {c.taskmaster_schedule_name} task started..")
    # T-O-D-O, the purpose of taskmaster job changed, this is obsolete
    #     so, we have a file of tasks to check
    # T-O-D-O-2 , schedulers should update sql table with available tasks
    # TODO 3, sql table is updated accordingly, task-retry part is actually the only todo here
    # tasks = g.read_from_tasks_json_file()['tasks']
    #   in theory, we only care about tasks that are new? what to do with in progress frozen/errored?
    #   let errored stay errored with some data
    #   let frozen.. hm. I need to check if there is a pool working on the task. if not, work with in progress too

    # we need a list of supported tasks
    directory_to_iterate = c.root_path + config['general']['tasks_folder']
    supported_tasks = []
    for filename in os.listdir(directory_to_iterate):
        f = os.path.join(directory_to_iterate, filename)
        # checking if it is a file
        if os.path.isfile(f):
            supported_tasks.append({'task_full_path': f, 'task_name': f.split('/')[-1].split('\\')[-1].split('.')[0]})
    # print(f"these are supported tasks from folder: {supported_tasks}")
    tasks_from_db = db_utils.select_from_table(c.taskmaster_tasks_table_name)
    # if there are tasks in db that are not valid, delete them from db
    # for t in tasks_from_db:
    #     pass

    for task in tasks_from_db:
        try:
            # if not route in routs_from_all_routes:
            if not task_is_in_tasks(task, supported_tasks):
                # delete rows with such tasks from db
                db_utils.delete_task_from_taskmaster_tasks_by_task_name(task['task_name'])
        except Exception as e:
            log.exception(f"Something went wrong while processing task(from db) {task}")
            log.exception(e)
    # 2. if route is in all_routes but not in db, add it (instead of add all below)
    for task in supported_tasks:
        try:
            if not task_is_in_tasks(task, tasks_from_db):
                # add to db
                db_utils.insert_into_table(c.taskmaster_tasks_table_name, task)
        except Exception as e:
            log.exception(f"Something went wrong while processing task(from files) {task}")
            log.exception(e)
    log.info(f"Taskmaster Tasks harvester finished job")


    #
    # for task in tasks:
    #     try:
    #         # check if we have such task at all
    #         if task['task_name'].split(c.tasks_name_delimiter)[0] in [t.split('//')[-1].split('\\')[-1].split('/')[-1].replace('.json', '') for t in supported_tasks]:
    #             task_file_path = [t for t in supported_tasks if task['task_name'].split(c.tasks_name_delimiter)[0] == t.split('//')[-1].split('\\')[-1].split('/')[-1].replace('.json', '')][0]
    #             task_file_content = g.read_from_json(task_file_path)
    #             treat_task_according_to_status(task, task_file_content)
    #         else:
    #             log.error(f"Task {task['task_name']} is not supported by this fuse.")
    #
    #     except Exception as e:
    #         log.exception(f"Something went horribly wrong while trying to process task {task['task_name']}")
    #         log.exception(e)


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
