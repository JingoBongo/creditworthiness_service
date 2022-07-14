import __init__
from utils import general_utils as g
from argparse import ArgumentParser
from utils import constants as c
from utils.flask_child import FuseNode
from utils import logger_utils as log
from utils.schedulers_utils import launch_taskmaster_scheduler_if_not_exists

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


@app.route('/tasks/start/<string:task_name>')
def start_task(task_name):
#     probably add new task to corresponding db table
#     so, table of tasks. TODO?  task name... I don't really like the idea of table.
#  json file? files_S_? more like it. one file for general hooks, then separate.. area? for more distinct files
# so, we only append a task with status 'open' to a file. how to make it concurrent?
# taskmaster threads can carry data in their  memory about steps statuses etc, and they can save intermediary
# states to pickles themselves.
# THEN, HERE WE START WITH JUST WRITING TO A FILE
    tasks = g.read_from_tasks_json_file()
    tasks['tasks'].append({"task_name": task_name, "status": "new"})
    g.write_tasks_to_json_file(tasks)
    return {"status": "ok", "msg" : f"task {task_name} sent to pool"}


if __name__ == "__main__":
    launch_taskmaster_scheduler_if_not_exists()
    app.run()
