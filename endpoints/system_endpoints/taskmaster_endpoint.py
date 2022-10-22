import socket
import threading

from flask import request, redirect, render_template

import __init__
from utils import general_utils as g, random_utils
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils import logger_utils as log
from utils.general_utils import init_start_function_process, read_from_tasks_json_file
from utils.pickle_utils import save_to_pickle, read_from_pickle
from utils.schedulers_utils import launch_taskmaster_scheduler_if_not_exists

from utils.taskmaster_utils import Input_Task, taskmaster_main_process

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


@app.route('/tasks/persistive-start/<string:task_name>', methods=['GET', 'POST'])
def persistive_task(task_name):
    task_unique_name = str(task_name) + c.tasks_name_delimiter + random_utils.generate_random_uid4()
    task_obj = Input_Task(task_name, task_unique_name)
    data = None
    if request.method == 'POST':
        data = request.get_json()
    result = []
    # TODO; such thread is not what I do rn. check lazy method for appropriate approach
    raise Exception('redo the shit')
    main_thread = threading.Thread(target=taskmaster_main_process, kwargs={'task_obj': task_obj, 'data': data, 'result':result})
    main_thread.start()
    main_thread.join()
    return str(result)



@app.route('/tasks/lazy-start/<string:task_name>', methods=['GET', 'POST'])
def lazy_task(task_name):
    task_unique_name = str(task_name) + c.tasks_name_delimiter + random_utils.generate_random_uid4()
    task_obj = Input_Task(task_name, task_unique_name)
    data = None
    if request.method == 'POST':
        data = request.get_json()
    # main_thread = threading.Thread(target=taskmaster_main_process, kwargs={'task_obj': task_obj, 'data': data})
    # main_thread.start()
    # we for sure change thread to a function.
    init_start_function_process(taskmaster_main_process, task_obj, data,
                                function_name=c.taskmaster_main_process_name+c.tasks_name_delimiter+task_unique_name)


    #  question rises. should it be a thread or a process? .... A PROCESS. removing todo tag, keep for  a while
    #  because 1) sometimes we will need to kill such things       ..... just as a comment
    #  2) we will need to store PIDs of PROCESSES in a db
    #  3) we will need a lot of computational power for it as well in theory.
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    # return {'status':'ok', 'msg':f"Task '{task_unique_name}' was sent to taskmaster.", 'context':f"{IPAddr}/redir/tasks/get_result/{task_unique_name}"}
    # return '<a href="' + IPAddr+ '/redir/tasks/get_result/' + task_unique_name+ '" target="_blank"> get result </a>'
    # return redirect(f"{IPAddr}/redir/tasks/get_result/{task_unique_name}")
    # return render_template('hyperlink.html', url = f"{IPAddr}/redir/tasks/get_result/{task_unique_name}")
    return redirect(f"http://{IPAddr}/redir/tasks/get_result/{task_unique_name}")
# TODO

#     TODO MAKE RESPONSE HAVE A LINK TO RESULT PAGE FOR LAZY



# TODO: clear all the TODOs that are outdated
# TODO: make tasks.json gitignorable, but recreate on launch
@app.route('/tasks/get_result/<string:task_unique_name>', methods=['GET', 'POST'])
def get_lazy_task_result(task_unique_name):
    tasks = read_from_tasks_json_file()
    for t in tasks['tasks']:
        if task_unique_name == t['task_unique_name']:
            if t['status'] == c.tasks_status_completed:
                try:
                    result = read_from_pickle(t['task_folder_path']+c.double_forward_slash+c.tasks_global_provides_file_name)
                    return {'status':t['status'], "result":result}
                except Exception as e:
                    log.exception(f"Something went horribly wrong while getting result of {task_unique_name}")
                    log.exception(e)
            else:
                # TODO this is temporary, I want to return error logs later
                return {"msg":f"Task status is: {t['status']}"}
    return {"msg":f"Task {task_unique_name} seems to not exist in tasks file"}


@app.route('/tasks/start/<string:task_name>')
def start_task(task_name):
    #     probably add new task to corresponding db table
    #     so, table of tasks. TODO?  task name... I don't really like the idea of table.
    #  json file? files_S_? more like it. one file for general hooks, then separate.. area? for more distinct files
    # so, we only append a task with status 'open' to a file. how to make it concurrent?
    # taskmaster threads can carry data in their  memory about steps statuses etc, and they can save intermediary
    # states to pickles themselves.
    # THEN, HERE WE START WITH JUST WRITING TO A FILE
    #
    #
    # new plan. act natural
    # get a task, if it is doable by framework, start worker and write into a file
    # scheduler will check if there are unfinished tasks, then it has sense AND can be done less frequently
    tasks = g.read_from_tasks_json_file()
    task_unique_name = str(task_name) + c.tasks_name_delimiter + random_utils.generate_random_uid4()
    task_obj = Input_Task(task_name, task_unique_name)
    tasks['tasks'].append(task_obj)
    g.write_tasks_to_json_file(tasks)

    return {"status": "ok", "msg": f"task {task_name} sent to pool"}


if __name__ == "__main__":
    launch_taskmaster_scheduler_if_not_exists()
    app.run()
