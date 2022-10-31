import __init__
import logging

import shutil
import socket

import json
import os
import psutil
import utils.read_from_yaml as yaml_utils
import sys
import utils.subprocess_utils as custom_subprocess
from utils import db_utils as db_utils
from utils import constants as c
from utils import logger_utils as log
from utils.random_utils import generate_random_uid4
import multiprocessing

db_name = 'main_db.db'
cur_file_name = os.path.basename(__file__)
config = yaml_utils.read_from_yaml(c.root_path + c.conf_path)
# busy_ports_json_path = c.root_path + config['general']['busy_ports_json_file']
# tasks_json_path = c.root_path + config['general']['tasks_json_file']
debug = config['general']['debug']
host = config['general']['host']
sql_engine_path = c.sql_engine_path


# def print_c(text):
#     # print(f"[{cur_file_name}] {str(text)}")
#     c.current_subprocess_logger.info(f"[{cur_file_name}] {str(text)}")


def run_cmd_command(command):
    # print_c(f'triggering command :{command}')
    log.info(f'triggering command :{command}')
    returned_value = os.system(command)
    # print_c(f'returned value: {returned_value}')
    log.info(f'returned value: {returned_value}')


def read_from_json(path: str):
    """
    try read data from json by path, in case of error gives blank JSON

    Args:
        path (str): path to file

    Returns:
        JSON dict with received data or blank JSON in case of error
    """
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except Exception as e:
        # print_c(f'Something went horribly wrong when attempted to read from file "{path}"')
        # print_c(e)
        log.exception(f'Something went horribly wrong when attempted to read from file "{path}"')
        log.exception(e)
        return {}


def write_to_json(path: str, text):
    """
    write data to json file

    Args:
        path (str): path to file where to save data
        text (any): data to save into json
    """
    try:
        with open(path, 'w') as outfile:
            json.dump(text, outfile)
    except Exception as e:
        log.exception(
            f'Something went horribly wrong when attempted to write into file "{path}" this specific text "{text}"')
        log.exception(e)


def clear_busy_ports():
    # new_json = {"busy_ports": []}
    # write_to_json(busy_ports_json_path, new_json)
    # log.info('Busy ports file cleared')
    db_utils.clear_table(c.busy_ports_table_name)


def clear_tasks_file():
    # new_json = {"tasks": []}
    # write_tasks_to_json_file(new_json)
    log.info('Tasks file cleared')


def reserve_ports_from_config():
    # busy_ports_json = read_from_json(busy_ports_json_path)
    # busy_ports_table = db_utils.select_from_table(c.busy_ports_table_name)
    # busy_ports_json['busy_ports'].append(str(port))
    # busy_ports = [p['port'] for p in busy_ports_table]
    services = config['services']['system'] | config['services']['business']
    for service_name, service_config in zip(services.keys(), services.values()):
        if services.get('port', None) is not None:
            # busy_ports_json['busy_ports'].append(str(service_config[service_name]['port']))
            db_utils.insert_into_table(c.busy_ports_table_name, {'port':service_config[service_name]['port']})

    # write_to_json(busy_ports_json_path, busy_ports_json)
    log.info('Ports from config were reserved')


# def read_from_tasks_json_file():
#     new_json = read_from_json(tasks_json_path)
#     return new_json
#
#
# def write_tasks_to_json_file(body):
#     write_to_json(tasks_json_path, body)
#     log.info(f"Updated tasks file")


def set_port_busy(port: int):
    # busy_ports_json = read_from_json(busy_ports_json_path)
    busy_ports_table = db_utils.select_from_table(c.busy_ports_table_name)
    busy_ports = [p['port'] for p in busy_ports_table]
    # int_port = int(port)
    if not port in busy_ports:
        db_utils.insert_into_table(c.busy_ports_table_name, {"port": port})
        # busy_ports_json['busy_ports'].append(str(port))
        # write_to_json(busy_ports_json_path, busy_ports_json)
        log.info(f"Set port {port} as busy")
    else:
        log.info(f"Did not set port {port} as busy")


#         TODO for some reason for predefined ports it says that it didn't set them busy, but it does it
#               maybe it does it before


def set_environment_variable(param, param1):
    os.environ[param] = str(param1)


def kill_process(pid):
    try:
        p = psutil.Process(int(pid))
        p.terminate()  # or p.kill()
    except:
        # print_c(f"Tried to kill process {pid}, it appears to be dead already")
        log.info(f"Tried to kill process {pid}, it appears to be dead already")


def get_rid_of_service_by_pid(pid):
    try:
        port_to_delete = db_utils.get_service_port_by_pid(pid)
        if port_to_delete:
            kill_process(pid)
            db_utils.delete_process_from_tables_by_pid(pid)
            db_utils.delete_port_from_busy_ports_by_port(port_to_delete)
            # print_c(f"Got rid of service with pid {pid} on port {port_to_delete}")
            log.info(f"Got rid of service with pid {pid} on port {port_to_delete}")
            return 'removed service'
        else:
            log.info(f"Couldn't get rid of service with pid {pid} because it does not belong to Fuse")
            return 'failed to removed service'
    except Exception as e:
        # print_c(e)
        log.exception(e)
        return 'failed to remove service'


def get_rid_of_service_by_pid_and_port_dirty(pid):
    try:
        kill_process(pid)
        # print_c(f"Got rid of service with pid {pid} dirty")
        log.info(f"Got rid of service with pid {pid} dirty")
        return 'removed service'
    except Exception as e:
        # print_c(e)
        log.exception(e)
        return 'failed to remove service dirty'


def start_service(service_short_name: str, service_full_path: str, port, local=False):
    local_part = ['-local', str(local)]
    port_part = ['-port', str(port)]
    local_process = custom_subprocess.start_service_subprocess(service_full_path, local_part, port_part,
                                                               service_short_name)
    log.info(f"fuse added service to pool: {service_short_name}")
    log.info(f"added path: {service_full_path}")
    return local_process


def check_port_is_in_use(port: int):
    # TODO check this in linux and mac
    used_str_ports = [str(line).split('port=')[1].split(')')[0] for line in psutil.net_connections()]
    if str(port) in used_str_ports:
        return True
    return False



def get_free_port():
    port_start_ind = config['fuse']['first_port']
    port_end_ind = config['fuse']['last_port']
    busy_ports_table = db_utils.select_from_table(c.busy_ports_table_name)
    # busy_ports_json = read_from_json(busy_ports_json_path)
    busy_ports = [p['port'] for p in busy_ports_table]
    for i in range(port_start_ind, port_end_ind + 1):
        if not i in busy_ports and not check_port_is_in_use(i):
            # if not (str_port in busy_ports_json['busy_ports']) and not check_port_is_in_use(str_port):
            log.info(f"Got new free port: {i}")
            return i
    log.exception(f"No ports found AT ALL; Something is really fucked up")


def check_file_exists(service_full_path: str):
    return os.path.exists(service_full_path)


def init_start_function_process(function, *args, function_name=None, **kwargs):
    # TODO; check if this if actually was necessary, cutting for now
    # if args or kwargs:
    p = custom_subprocess.CustomNamedProcess(target=function, args=args, name=function_name, kwargs=kwargs)
    # TODO this stores function ref? in db? is this ok?
    dic = {'arguments': str(args).join(str(kwargs))}

    # else:
    #     p = multiprocessing.Process(target = function)
    p.start()

    dic['function_name'] = str(function_name) if function_name else function.__name__
    dic['pid'] = p.pid

    # TODO, in future kill by PID, but check process in new all processes table, not in sys/business ones
    db_utils.insert_into_table(c.all_processes_table_name, dic)
    return p


def init_start_service_procedure(service: str, is_sys=False):
    # TODO. HERE must be checker if file path exists
    type = 'system' if is_sys else 'business'
    service_full_path = c.root_path + config['services'][type][service]['path']

    if not check_file_exists(service_full_path):
        log.error(f"Service '{service}' has no existing file in path '{service_full_path}")
        return

    service_config = config['services'][type][service]

    #   port verification
    port: int = service_config.get('port', None)
    if port is None or not isinstance(port, int) or port <= 0:
        port = get_free_port()
    set_port_busy(port)

    local = service_config.get('local', None)
    spawn_type = service_config.get('mono', None)
    #     TODO when mono/multi becomes a things, add that info to arguments

    if spawn_type != "multi":
        if local:
            new_process = start_service(service, service_full_path, port, local=local)
        else:
            new_process = start_service(service, service_full_path, port)
    else:
        raise Exception('Implement multi endpoint stuff')
    if is_sys:
        db_utils.insert_into_sys_services(service, service_full_path, port, new_process.pid)
    else:
        db_utils.insert_into_business_services(service, service_full_path, port, new_process.pid)

    lis = [{"port": port}, {"local": local}]
    dic = {'pid': new_process.pid, 'pyfile_path': service_full_path, 'pyfile_name': service, 'arguments': str(lis)}

    # TODO for noqw clear all processes on start
    db_utils.insert_into_table(c.all_processes_table_name, dic)


def process_start_service(service_name: str):
    try:
        service_config = config['services']['system'].get(service_name, None)
        if service_config is not None:
            init_start_service_procedure(service_name, is_sys=True)
            return 'service started'
        service_config = config['services']['business'].get(service_name, None)
        if service_config is not None:
            init_start_service_procedure(service_name, is_sys=False)
            return 'service started'
    except Exception as e:
        log.exception(e)
        return 'service failed to start'


def check_fuse_logger_file_is_current_logger(filepath):
    fuse_name = 'abobacadabra99912299939993999499959'
    for key in logging.root.manager.loggerDict.keys():
        if 'fuse-' + str(os.getpid()) in key:
            fuse_name = key
    if fuse_name == filepath:
        return True
    return False


def remove_folder_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            log.info(f"Cleared contents of '{folder}' folder")
        except Exception as e:
            # print('Failed to delete %s. Reason: %s' % (file_path, e))
            log.exception('Failed to delete %s. Reason: %s' % (file_path, e))


def clear_log_folder():
    log_folder_name = c.root_path + 'resources//' + c.logs_folder_name
    remove_folder_contents(log_folder_name)


def recreate_log_folder_if_not_exists():
    log_folder_name = c.root_path + 'resources//' + c.logs_folder_name
    isExist = os.path.exists(log_folder_name)

    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(log_folder_name)
        # log.info(f"Recreated log folder")


def generate_on_start_unique_fuse_id():
    # TODO, unique ID is NOT sent to constants of other processes; fix
    c.on_start_unique_fuse_id = c.fuse_instance_name + '-' + generate_random_uid4()
    # db_utils.bulk_upsert_common_strings_table(c.on_start_unique_fuse_id_name, c.on_start_unique_fuse_id)
    # db_utils.delete_port_from_busy_ports_by_port
    # db_utils.delete_value_by_key_from_common_strings()
    db_utils.upsert_key_value_pair_from_common_strings_table(c.on_start_unique_fuse_id_name, c.on_start_unique_fuse_id)