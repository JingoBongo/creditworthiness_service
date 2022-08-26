import __init__
from utils import constants as c

class Input_Task:
    task_name = None
    task_unique_name = None
    status = c.tasks_status_new

    def __init__(self, t_name, t_unique_name):
        self.task_name = t_name
        self.task_unique_name = t_unique_name


def taskmaster_main_process(task_obj: Input_Task, data, result = None):
    # first 'if' in lazy_task case; then save overall result in specific pickle
    if not result:
        pass
    # second else for persistive case
    else:
        pass
#     check if such task exists.

