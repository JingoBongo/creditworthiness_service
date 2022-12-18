from flask import request

import __init__

from argparse import ArgumentParser

from utils.decorators.cors import crossdomain
from utils.flask_child import FuseNode
from utils.general_utils import get_rid_of_service_by_pid, process_start_service
from utils.general_utils import get_rid_of_service_by_pid_and_port_dirty, db
from utils.schedulers_utils import launch_life_ping_scheduler_if_not_exists
from utils import constants as c

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
    if len(db.select_from_table_by_one_column(c.all_processes_table_name, 'pid', pid, 'Integer')) != 1:
        return "Provided pid is not owned by the Fuse, therefore aborting"
    if isinstance(pid, int) and pid > 0:
        return get_rid_of_service_by_pid(pid)
    else:
        return "Input valid pid, please be aware that you can kill actual windows process"
@crossdomain(origin='*')
@app.route('/services/remove/', methods=["POST"])
def get_rid_of_service_post():
    """Removes a service. provide with pid
    Be aware that this kills ANY process by PID, not only fuse's one
        ---
    responses:
      200:
        description: 99% caution
    """
    pid = int(request.args.get("pid"))
    if len(db.select_from_table_by_one_column(c.all_processes_table_name, 'pid', pid, 'Integer')) != 1:
        return "Provided pid is not owned by the Fuse, therefore aborting"
    if isinstance(pid, int) and pid > 0:
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
    return process_start_service(service_name)


#
# TODO make a task to relaunch X service

if __name__ == "__main__":
    launch_life_ping_scheduler_if_not_exists()
    app.run()
