from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g

class Input_Task:
    task_name = None
    task_unique_name = None
    status = c.tasks_status_new

    def __init__(self, t_name, t_unique_name):
        self.task_name = t_name
        self.task_unique_name = t_unique_name