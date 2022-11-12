import __init__
from utils import constants as c



class InputTask:
    __slots__ = ("task_name", "task_unique_name", "status")
    # task_name = None
    # task_unique_name = None
    # status = c.tasks_status_new

    def __init__(self, t_name, t_unique_name):
        self.task_name = t_name
        self.task_unique_name = t_unique_name
        self.status = c.tasks_status_new
