import __init__
import socket
from flask import request, redirect, render_template

from utils import general_utils as g, random_utils
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils import logger_utils as log
from utils.pickle_utils import read_from_pickle
from utils.schedulers_utils import launch_taskmaster_scheduler_if_not_exists
from utils import db_utils as db

from utils.taskmaster_utils import InputTask, do_the_task

parser = ArgumentParser()
app = FuseNode(__name__, template_folder=c.root_path + c.templates_folder_name, arg_parser=parser)


@app.route('/')
def hello():
    """Root, please go somewhere else
    ---
    responses:
      200:
        description: why would you go here, go away
    """
    return 'system endpoint'


@app.route('/tasks/start/redirect-to-result/<string:task_name>', methods=['GET', 'POST'])
def lazy_task(task_name):
    """Start task and redirect to result
    ---
    responses:
      200:
        description: 99% caution
    """
    log.info(f"Started working on task {task_name}")
    task_unique_name = str(task_name) + c.tasks_name_delimiter + random_utils.generate_random_uid4()
    task_obj = InputTask(task_name, task_unique_name)
    data = None
    if request.method == 'POST':
        data = request.get_json()

    do_the_task(task_obj, data)

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # why didn't I just use localhost here?)..
    return redirect(f"http://{ip_address}/redir/tasks/get_result/{task_unique_name}")


@app.route('/tasks/get_result/<string:task_unique_name>', methods=['GET'])
def get_lazy_task_result(task_unique_name):
    """Get task result
    ---
    responses:
      200:
        description: 99% caution
    """
    task_from_db = db.select_from_table_by_one_column(c.tasks_table_name, 'task_unique_name', task_unique_name,
                                                      'String')
    if len(task_from_db) == 1:
        task_from_db = task_from_db[0]
        if task_from_db['status'] == c.tasks_status_completed:
            try:
                result = read_from_pickle(
                    task_from_db['task_folder_path'] + c.double_forward_slash + c.tasks_global_provides_file_name)
                return {'status': task_from_db['status'], "result": result}
            except Exception as e:
                log.exception(f"Something went horribly wrong while getting result of {task_unique_name}")
                log.exception(e)
        else:
            # TODO this is temporary, I want to return error logs later
            return {"msg": f"Task status is: {task_from_db['status']}"}
    else:
        return {"msg": f"Task {task_unique_name} seems to not exist in tasks file"}


@app.route('/tasks/start/return-url-to-result/<string:task_name>')
def start_task(task_name):
    """Start task and return url to result
    ---
    responses:
      200:
        description: 99% caution
    """
    log.info(f"Started working on task {task_name}")
    task_unique_name = str(task_name) + c.tasks_name_delimiter + random_utils.generate_random_uid4()
    task_obj = InputTask(task_name, task_unique_name)
    data = None
    if request.method == 'POST':
        data = request.get_json()

    do_the_task(task_obj, data)
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    result_url = f"http://{ip_address}/redir/tasks/get_result/{task_unique_name}"
    return {"status": "ok", "msg": f"task {task_name} sent to pool", "result_url": result_url}


if __name__ == "__main__":
    print(f'Taskmaster endpoint main')
    launch_taskmaster_scheduler_if_not_exists()
    app.run()
