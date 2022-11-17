import __init__

from utils import constants as c
from utils import logger_utils as log
from utils.dataclasses.task_step_from_file import TaskStepFromFile
from utils.json_utils import read_from_json


class TaskFromFile:
    __slots__ = ("task_name", "task_unique_name", "init_requires", "global_provides", "task_folder_path", "steps",
                 "finished_steps", "status", "error_logs", "is_threaded")

    def __init__(self, task_file_path, task_unique_name, data):
        task_dict_from_file = read_from_json(task_file_path)
        self.task_name = task_dict_from_file['task_name']
        self.task_unique_name = task_unique_name
        # So here we do a bit of trolling. data is actually what user sends.
        # init requires is what task NEEDS. so we will make enough checks
        # 0.5. Len of init <= data keys
        # 1. There are enough keys in data
        data_keys = []
        if data and data.keys():
            data_keys = data.keys()
        temp_init_requires_keys = []
        if task_dict_from_file['init_requires']:
            temp_init_requires_keys = task_dict_from_file['init_requires']

        self.check_there_are_enough_init_variables(temp_init_requires_keys, data_keys)
        self.check_if_needed_argument_keys_provided(temp_init_requires_keys, data_keys)
        # 2. we loop through init requires because client can send extra data that we don't need
        temp_init_requires_dict = {}
        for key in temp_init_requires_keys:
            temp_init_requires_dict[key] = data[key]

        self.init_requires = {}
        self.init_requires.update(temp_init_requires_dict)
        self.global_provides = {}
        self.global_provides.update(temp_init_requires_dict)

        self.task_folder_path = None
        self.steps = []
        self.finished_steps = []
        for s in task_dict_from_file['steps']:
            new_step = TaskStepFromFile(step_number=s['step_number'],
                                        step_name=s['step_name'],
                                        service=s['service'],
                                        route=s['route'],
                                        request_type=s['request_type'],
                                        requires=s['requires'],
                                        requires_steps=s['requires_steps'],
                                        needs_to_provide=s['provides'])
            self.steps.append(new_step)
        self.status = c.tasks_status_new
        self.error_logs = None
        self.is_threaded = True if len(self.steps) <= c.tasks_steps_number_to_make_a_process else False

    @staticmethod
    def check_there_are_enough_init_variables(temp_init_requires, data_keys):
        if len(temp_init_requires) > len(data_keys):
            log.error(
                f"Failed to create {TaskFromFile.__name__}; Task needed next arguments:{temp_init_requires}, but got: {data_keys}")
            raise Exception(
                f"Failed to create {TaskFromFile.__name__}; Task needed next arguments:{temp_init_requires}, but got: {data_keys}")

    @staticmethod
    def check_if_needed_argument_keys_provided(temp_init_requires, data_keys):
        for key in temp_init_requires:
            if key not in data_keys:
                log.error(
                    f"Failed to create {TaskFromFile.__name__}; Task needed argument:{key}, but got: {data_keys}")
                raise Exception(
                    f"Failed to create {TaskFromFile.__name__}; Task needed argument:{key}, but got: {data_keys}")
