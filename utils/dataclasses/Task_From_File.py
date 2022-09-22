from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g
from utils.dataclasses.Task_Step_From_File import Task_Step_From_File


class Task_From_File:
    def __init__(self, task_file_path, task_unique_name):
        task_dict_from_file = g.read_from_json(task_file_path)
        self.task_name = task_dict_from_file['task_name']
        self.task_unique_name = task_unique_name
        # self.init_requires = []
        self.init_requires = [].extend(task_dict_from_file['init_requires'])
        # TODO: if local requires ends up useless and just goes into global provides, maybe just cut it?
        # self.global_provides = []
        self.global_provides = [].extend(task_dict_from_file['init_requires'])
        self.steps = []
        self.task_folder_path = None
        self.finished_steps = []
        for s in task_dict_from_file['steps']:
            new_step = Task_Step_From_File(step_number=s['step_number'],
                                           step_name=s['step_name'],
                                           service=s['service'],
                                           route=s['route'],
                                           request_type=s['request_type'],
                                           requires=s['requires'],
                                           requires_steps=s['requires_steps'])
            self.steps.append(new_step)
            self.status = c.tasks_status_new
            self.error_logs = None