import json

from flask import request

import __init__

from argparse import ArgumentParser

from utils.decorators.cors import crossdomain
from utils.flask_child import FuseNode
from utils.general_utils import get_rid_of_service_by_pid, process_start_service
from utils.general_utils import get_rid_of_service_by_pid_and_port_dirty, db
from utils.schedulers_utils import launch_life_ping_scheduler_if_not_exists
from utils import constants as c, db_utils
from utils import logger_utils as log
from utils.yaml_utils import get_config, save_config, set_service_enabled

parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/schedulers/statuses')
def get_shedulers_list():
    """Shows list of schedulers. No arguments needed.
        ---
    responses:
      200:
           description: 99% caution
        """
    return str(db.select_from_table('schedulers'))


@app.route('/services/statuses')
def get_services_list():
    """Shows list of services. No arguments needed.
        ---
    responses:
      200:
        description: 99% caution
        """
    return str(db.select_from_table('Business_services') + db.select_from_table('Sys_services'))


@crossdomain(origin='*')
@app.route('/services/remove/<int:pid>', methods=["GET"])
def get_rid_of_service(pid):
    """Removes a service. provide with pid
    Be aware that this kills ANY process by PID, not only fuse's one
        ---
    responses:
      200:
        description: 99% caution
    """
    # TODO: also set as disabled in config.. somehow
    if len(db.select_from_table_by_one_column(c.all_processes_table_name, 'pid', pid, 'Integer')) != 1:
        return "Provided pid is not owned by the Fuse, therefore aborting"
    if isinstance(pid, int) and pid > 0:
        all_servces = db_utils.select_from_table(c.sys_services_table_name) + db_utils.select_from_table(
            c.business_services_table_name)
        service_name = [service for service in all_servces if int(service['pid']) == pid][0]['name']
        set_service_enabled(service_name, False)
        return get_rid_of_service_by_pid(pid)
    else:
        return "Input valid pid, please be aware that you can kill actual windows process"


# TODO make these duplicates the right way, not just the working way
@crossdomain(origin='*')
@app.route('/services/remove_post', methods=["POST"])
def get_rid_of_service_post():
    # Accepts JSON!
    """Removes a service. provide with pid
    Be aware that this kills ANY process by PID, not only fuse's one
        ---
    responses:
      200:
        description: 99% caution
    """
    pid = int(request.get_json()["pid"])

    if len(db.select_from_table_by_one_column(c.all_processes_table_name, 'pid', pid, 'Integer')) != 1:
        return "Provided pid is not owned by the Fuse, therefore aborting"
    if isinstance(pid, int) and pid > 0:
        all_servces = db_utils.select_from_table(c.sys_services_table_name) + db_utils.select_from_table(
            c.business_services_table_name)
        service_name = [service for service in all_servces if int(service['pid']) == pid][0]['name']
        set_service_enabled(service_name, False)
        return get_rid_of_service_by_pid(pid)
    else:
        return "Input valid pid, please be aware that you can kill actual windows process"


@app.route('/services/remove-dirty/<int:pid>')
def remove_service_wrong(pid):
    """Removes a service 'dirty' to trigger life ping revival. provide with pid
        Be aware that this kills ANY process by PID, not only fuse's one
        ---
    responses:
      200:
        description: 99% caution
    """
    if not len(db.select_from_table_by_one_column(c.all_processes_table_name, 'pid', pid, 'Integer')) == 1:
        return "Provided pid is not owned by the Fuse, therefore aborting"
    if isinstance(pid, int) and pid > 0:
        return get_rid_of_service_by_pid_and_port_dirty(pid)
    else:
        return "Input valid pid, please be aware that you can kill actual windows process"


@crossdomain(origin='*')
@app.route('/services/start/<service_name>')
def start_service(service_name):
    """Starts a service. provide with service name from config..
            ---
        responses:
          200:
            description: 99% caution
        """
    set_service_enabled(service_name, True)
    return process_start_service(service_name)


@crossdomain(origin='*')
@app.route('/services/start_post', methods=["POST"])
def start_service_post():
    """Starts a service. provide with service name from config..
            ---
        responses:
          200:
            description: 99% caution
        """
    service_name = str(request.get_json()["name"])
    # TODO: also enable in config
    set_service_enabled(service_name, True)
    # TODO add this to GET version of request
    return process_start_service(service_name)


@crossdomain(origin='*')
@app.route('/config/get_disabled_services')
def config_get_disabled_services():
    """Starts a service. provide with service name from config..
            ---
        responses:
          200:
            description: 99% caution
        """
    config = get_config()
    system_services = config['services']['system']
    business_services = config['services']['business']
    return_list = []
    for k, v in system_services.items():
        if v.get('enabled', None):
            return_list.append({"name": k, "path": v["path"]})
    for k, v in business_services.items():
        if v.get('enabled', None):
            return_list.append({"name": k, "path": v["path"]})
    return return_list


@crossdomain(origin='*')
@app.route('/config/get_disabled_services_dict')
def config_get_disabled_services_dict():
    """Starts a service. provide with service name from config..
            ---
        responses:
          200:
            description: 99% caution
        """
    config = get_config()
    system_services = config['services']['system']
    business_services = config['services']['business']

    return_list = []
    for k, v in system_services.items():
        # TODO: check in other places. v.get[enabled, none] gives false on positives
        if 'enabled' in v.keys():
            if not v['enabled']:
                return_list.append({"name": k, "path": v["path"]})
    for k, v in business_services.items():
        if 'enabled' in v.keys():
            if not v['enabled']:
                return_list.append({"name": k, "path": v["path"]})
    return json.dumps(return_list)


#
# TODO make a task to relaunch X service

# TODO: in services UI change db_utils call to call from here when getting 2 tables of services

if __name__ == "__main__":
    launch_life_ping_scheduler_if_not_exists()
    app.run()
