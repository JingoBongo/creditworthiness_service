import concurrent
from concurrent.futures import ThreadPoolExecutor

import __init__
from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g
from utils import db_utils as db
import concurrent.futures


class Input_Task:
    task_name = None
    task_unique_name = None
    status = c.tasks_status_new

    def __init__(self, t_name, t_unique_name):
        self.task_name = t_name
        self.task_unique_name = t_unique_name


class Task_Step_From_File:
    def __init__(self, step_number, step_name, service, route, request_type, requires, requires_steps):
        self.step_number = step_number
        self.step_name = step_name
        self.service = service
        self.route = route
        self.request_type = request_type
        self.requires = []
        self.requires.extend(requires)
        self.requires_steps = []
        self.requires_steps.extend(requires_steps)
        self.is_finished = False


class Task_From_File:
    def __init__(self, task_file_path, task_unique_name):
        task_dict_from_file = g.read_from_json(task_file_path)
        self.task_name = task_dict_from_file['task_name']
        self.task_unique_name = task_unique_name
        # self.init_requires = []
        self.init_requires = [].append(task_dict_from_file['init_requires'])
        # TODO: if local requires ends up useless and just goes into global provides, maybe just cut it?
        # self.global_provides = []
        self.global_provides = [].append(task_dict_from_file['init_requires'])
        self.steps = []
        for s in task_dict_from_file['steps']:
            new_step = Task_Step_From_File(step_number = s['step_number'],
                                           step_name = s['step_name'],
                                           service = s['service'],
                                           route = s['route'],
                                           request_type = s['request_type'],
                                           requires = s['requires'],
                                           requires_steps = s['requires_steps'])
            self.steps.append(new_step)
            self.status = c.tasks_status_new
            self.error_logs = None


#         TODO: still, we probably need to parse these into ALL_requires; better in global_provides(yes)
#       TODO: so basically requires means a LOCAL list that endpoint expects to get.
#           GLOBAL PROVIDES has literally all key-values pairs, LOCAL PROVIDES means what step will ADD to global one


def task_is_in_tasks(task, tasks_from_db):
    #     route and function_name, service_name, route
    for ttask in tasks_from_db:
        if task['task_full_path'] == ttask['task_full_path'] and task['task_name'] == ttask['task_name']:
            return True
    #           here we purely assume that duplicates do not exist in harvested route table
    return False


def process_task_step(task, index):
    print(f"I am inside process new step {index}")

def process_new_task(task):
    #     now we need to find if this fuse supports needed task
    # change status of task with unique name to in progress
    with ThreadPoolExecutor() as executor:
        [executor.map(process_task_step, (i, task)) for i in range(1, len(task.steps))]
    executor.shutdown(wait=True)
    print('I am inside process new task')
    # old_val_tasks = g.read_from_tasks_json_file()
    # for t in old_val_tasks['tasks']:
    #     if task['task_name'] == t['task_name']:
    #         t['status'] = c.tasks_status_in_progress
    #         break
    # g.write_tasks_to_json_file(old_val_tasks)
    # start making tasks in a pool?


def process_task_in_progress(task, task_file_content):
    log.error(f"Implement me: process_task_in_progress!!!!")



def treat_task_according_to_status(task, task_file_content):
    if task['status'] == c.tasks_status_new:
        process_new_task(task)
    elif task['status'] == c.tasks_status_in_progress:
        process_task_in_progress(task, task_file_content)
    else:
        log.info(
            f"Task {task['task_name']} was ignored by taskmaster scheduler since it was not 'new' or 'in progress'")


def taskmaster_main_process(input_task_obj: Input_Task, data, result=None):
    # first 'if' in lazy_task case; then save overall result in specific pickle
    if not result:
        pass
    # second else for persistive case
    else:
        pass
    #     check if such task exists.
    #   long story short here the code starts
    #   1. check if such task type exists, return(?) error if not
    task_type_from_db = db.select_from_table_by_one_column(c.taskmaster_tasks_table_name,
                                                           "task_name",
                                                           input_task_obj.task_name,
                                                           "String")
    if len(task_type_from_db) == 1:
        task_type_from_db = task_type_from_db[0]
        #       such task exists, next check
        #   TODO, what check do we expect if len of tasks from db is >1?
        #   2. check if task needs input data, return(?) error if there is no input data
        #     TODO, for that I need proper task object
        #   3. process the steps in gevent(?), in a thread pool
        #   4. ...? result bla bla bla?..
        task = Task_From_File(task_type_from_db['task_full_path'], input_task_obj.task_unique_name)
        # tasks file needs only task name, task unique name and generated from start thingy
        new_dict_task = {"task_name": input_task_obj.task_name, "task_unique_name" : input_task_obj.task_unique_name,
                         c.on_start_unique_fuse_id_name : c.on_start_unique_fuse_id,
                         "status" : c.tasks_status_new}
        g.write_tasks_to_json_file(new_dict_task)
        # TODO, what exact variables I need once again?
        # step-Local and global provides for sure; what about 2 task_names? the code only cares about the file name anyways
        # THEN, I am SURE the better and more compact way is to save all vars from steps, therefore no need in provides at all
        # I don't really need in progress status then? I mean frozen tasks from scheduler are checked w/ to fuse_id;;; no, I want statuses. Status to in progress will be set
        # here; done or errored after threadpool finishes. So in future we can rerun failed or whatever. and that is actually done ABOVE, you blind shit
        # But, I'd add task status as a property
        # TODO but, in case names overlap, what to do? Handle by putting them under test_step_index_---variable_key_name

        process_new_task(task)

    #     small update to everything below. keeping track of what tasks are from previous run == using unique fuse uuid
    #     we are going to use threadpool / gevent so no need for a file, output of steps will be stored in unique pickles
    #       anyway
    #     errored tasks should stay errored. there should be an endpoint with the list of all current tasks for better use
    #     and if there is a table with tasks, then use db endpoint probably


    #     TODO add in-progress-task to a file? to db? I kinda want in in a file
    #     TODO, it means scheduler will need to check that file. How to get clue that task was abandoned?
    #     TODO, task will havew a unique string that is generated each time Fuse is started, therefore
    #     TODO, anything that has different UUID is from previous era.
    #     TODO, But how to catch errored tasks? just frozen tasks? Errored should stay errored i think, with an option
    #     TODO, to retry them with same data, THIS IS WHY WE NEED INIT_REQUIRES (as a pickle)
    #     TODO:: Frozen tasks.. We need a way to kill them. start task work in a new process and kill it in case of emergency?
    #     TODO we can just kill the thread if it is somehow STORED/MARKED ==> store PROCESSESS?
    else:
        log.error(f"There are no such tasks supported by this Fuse.")
        log.error(f"Supported tasks: {task_type_from_db}")
#         TODO, how to report human mistake/errors?


# TODO : how about a check and retry at the end of the task execution in case for steps that did not fall into 'done' list
# TODO done list should be a file in case of emergency shut down
# TODO there should be a way to return 'error' in case some steps failed, but also return which steps succeeded and which didn't
# TODO LEARN and see if GEVENTS would be of good use
