import __init__
from itertools import repeat
import time
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor
from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g
from utils import db_utils as db
from utils.dataclasses.Input_Task import Input_Task
from utils.dataclasses.Task_From_File import Task_From_File
from utils.dataclasses.Task_Step_From_File import Task_Step_From_File
from utils.general_utils import read_from_tasks_json_file, kill_process
from utils.pickle_utils import save_to_pickle, read_from_pickle
from utils import client_utils


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


def end_task_procedure(task: Task_From_File, error_reason):
    log.error(error_reason)
    task.status = c.tasks_status_errored
    tasks_from_json = read_from_tasks_json_file()
    for t in tasks_from_json['tasks']:
        if t['task_unique_name'] == task.task_unique_name:
            t['status'] = c.tasks_status_errored
    task.error_logs = error_reason
    log.error(f"Exiting task {task.task_unique_name}, saving task fallback object")
    #     save pickle with task
    save_to_pickle(task.task_path + '//' + c.tasks_errored_fallback_file_name, task)
    # get pid of current process, first find it in db
    process_from_db = db.select_from_table_by_one_column(c.all_processes_table_name, 'function_name',
                                                         c.taskmaster_main_process_name + c.tasks_name_delimiter + task.task_unique_name,
                                                         'String')
    if not process_from_db or not len(process_from_db) == 1:
        log.error(
            f"There were somehow more or none processes with this unique taskname "
            f"{c.taskmaster_main_process_name + c.tasks_name_delimiter + task.task_unique_name}, aborting killing it by PID")
        return
    process_from_db = process_from_db[0]
    db.delete_process_from_tables_by_pid(process_from_db['pid'])
    kill_process(process_from_db['pid'])


# remove process from db

# in all processes table I can't find needed process; solved, removing TODO

# kill process. lul, i wonder how it would work if a process kills itself

def prepare_data_for_post_request(task, needed_keys):
    if needed_keys and len(needed_keys) > 0:
        provided_keys_from_init_requires = task['init_requires']
        for key in needed_keys:
            if key not in provided_keys_from_init_requires.keys():
                end_task_procedure(task,
                                   f"Task {task['task_unique_name']} ended early as required {key} was not provided")
        needed_data = {}
        for key in needed_keys:
            # i think here we should update with new dict, not just value
            needed_data.update({key: task.global_provides[key]})
        return needed_data

    #     {
    #   "step_number" : 1,
    #   "step_name" : "clear harvester table",
    #   "service" : "db_endpoint",
    #   "route" : "/clear/Harvested_Routes",
    #   "request_type": "GET",
    #   "requires" : [],
    #   "requires_steps": []
    # },


def required_steps_arent_finished(required_steps, task: Task_From_File):
    for step in required_steps:
        if not step in task.finished_steps:
            return True
    return False


def process_step(task: Task_From_File, index):
    # cover step in try catch?
    print(f"I am inside process new step {index}")
    local_step: Task_Step_From_File = task.steps[index - 1]

    # sleep untill needed steps are finished
    if local_step.requires_steps and isinstance(local_step.requires_steps, list):
        while required_steps_arent_finished(local_step.requires_steps, task):
            time.sleep(1)

    # grand note here. we don't need additional data and even check for it if we have a GET request
    # TODO: I forgot to implement "step getting data from requires or from provides"
    data_for_post = None
    data_type = None
    if local_step.request_type == c.request_type_post:
        needed_keys = local_step['requires']
        data_for_post = prepare_data_for_post_request(task, needed_keys)
        data_type = {'Content-Type': 'application/json'}

    # we should be able to send request now. if we use post request, add content type json
    resp = client_utils.init_send_request(service=local_step.service, context=local_step.route,
                                          #   request_type=local_step.request_type, headers=headers, where to get headers?
                                          request_type=local_step.request_type,
                                          data=data_for_post, claimed_data_type=data_type)
    if len(local_step.needs_to_provide) > 0:
        local_dict = {}
        if 'application/json' in resp.headers.get('Content-Type'):
            try:
                for key in local_step.needs_to_provide:
                    content_to_save = {local_step.step_number + c.tasks_step_provides_delimiter + key: resp.json()[key]}
                    local_dict.update(content_to_save)
                    # task.global_provides[local_step.step_number + c.tasks_step_provides_delimiter + key] = resp.json()[key]
                # task.global_provides.update(local_dict)
            except Exception as e:
                end_task_procedure(task, e)
        elif isinstance(resp.content, dict):
            try:
                for key in local_step.needs_to_provide:
                    content_to_save = {local_step.step_number + c.tasks_step_provides_delimiter + key : resp.content[key]}
                    local_dict.update(content_to_save)
                    # task.global_provides.update(content_to_save)
                # task.global_provides
            except Exception as e:
                end_task_procedure(task, e)
        elif isinstance(resp.content, str):
            if len(local_step.needs_to_provide) == 1:
                key = local_step.needs_to_provide[0]
                content_to_save = {local_step.step_number + c.tasks_step_provides_delimiter + key : resp.content}
                # task.global_provides.update(content_to_save)
            else:
                end_task_procedure(task,
                                   "If response content type is string, step should only provide one key-value pair set in schema file")
        else:
            end_task_procedure(task, "Response body is not JSON, dict or string, what is that?")
        task.global_provides.update(content_to_save)
        save_to_pickle(task.task_folder_path + '//' + local_step.step_number + c.tasks_step_provides_delimiter + 'response', local_dict)
    task.finished_steps.append(local_step.step_number)
    print('debug point')


# next, if response is fine try to get needed provides keys from there. if we don't get dict, try to
# save as one key-value pair;
# TODO: don't forget to add step index to the pickle and to move step to finished
# TODO: add status check in request method

# TODO client utils for get and post requests

# TODO send post request, get response,
#     TODO set all key-value pairs inside provides
#     TODO save pickleS, local-step and global provides
#     TODO add step to finished
#     TODO report in logs about finish
#     TODO cover entire step in try catch, in catch I guess we put task to failed

# TODO, we should def. check for file size of what we get in taskmaster. Where? How? How much?
# if prev. step is not completed, wait for it, so a loop while we sleep and wait


#
#     So, for this part we need Client utils or whatever to send requests that we need
#     TODO, cover every freaking bit in try catch and complete error_logs in catch?
#     Then we collect the result both in temp step pickle and in overall pickle
#     If i recall right we either add step to lists of completed steps

#     in the step execution end put the index in the list of finished steps

def process_new_task(task: Task_From_File):
    #     now we need to find if this fuse supports needed task  << already happened before we started
    # change status of task with unique name to in progress << done below

    # TODO, write methods to update json tasks according to unique name instead of what i do below
    # TODO, add to schedulers to check for leftover files after tasks? for how long do we store them?
    json_file_tasks = g.read_from_tasks_json_file()
    for t in json_file_tasks['tasks']:
        if t['task_unique_name'] == task.task_unique_name:
            t['status'] == c.tasks_status_in_progress
    g.write_tasks_to_json_file(json_file_tasks)
    task.status = c.tasks_status_in_progress

    # TODO, add directory (I think in task obj as well (path))
    # here we add folder to resources and
    task.task_folder_path = c.temporary_files_folder_path + '//' + str(task.task_unique_name)
    Path(task.task_folder_path).mkdir(parents=True, exist_ok=True)
    log.info(f"Created folder '{task.task_folder_path}' for the task to execute")

    # TODO now is the time to create init_requires if needed
    if task.init_requires and isinstance(task.init_requires, list) and len(task.init_requires) > 0:
        save_to_pickle(task.task_folder_path + '//' + c.tasks_init_requires_file_name, task.init_requires)
    # TODO And global_provides pickle
    save_to_pickle(task.task_folder_path + '//' + c.tasks_global_provides_file_name, {})

    with ThreadPoolExecutor(max_workers=len(task.steps)) as executor:
        for result in executor.map(process_step, repeat(task), range(1, len(task.steps) + 1)):
            pass
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
    log.get_log(f"taskmaster_task_process")
    if not result:
        pass
    # TODO second else for persistive case
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
        task = Task_From_File(task_type_from_db['task_full_path'], input_task_obj.task_unique_name, data)

        # tasks file needs only task name, task unique name and generated from start thingy... a status maybe
        new_dict_task = {"task_name": input_task_obj.task_name, "task_unique_name": input_task_obj.task_unique_name,
                         c.on_start_unique_fuse_id_name: c.on_start_unique_fuse_id,
                         "status": c.tasks_status_new}
        tasks_file = g.read_from_tasks_json_file()
        tasks_file['tasks'].append(new_dict_task)
        g.write_tasks_to_json_file(tasks_file)
        # TODO but, in case names (of vars?) overlap, what to do? Handle by putting them under test_step_index_---variable_key_name
        process_new_task(task)
    #     there should be an endpoint with the list of all current tasks for better use
    #     and if there is a table with tasks, then use db endpoint probably
    #      I actually think we need to store fuse unique id in Task object as well. Why? to save it in pickle for fallback. Why? not sure.
    #         Nononononononono. We recreate object from pickle, right? But indexing point should be tasks file so we don't browse entire temp folder

    #     TODO add in-progress-task to a file? to db? I kinda want in in a file ;;;; discuss about it being in db. we can't really inspect db while fuse is stopped
    #     TODO, then file only? duplicate it in db a well?
    #     TODO  in case internal logic requires it, keep it in db as well.

    #     TODO How to get clue that task was abandoned?
    #     TODO, anything that has different UUID is from previous era.
    #     TODO, But how to catch errored tasks? just frozen tasks? Errored should stay errored i think, with an option
    #     TODO, to retry them with same data, THIS IS WHY WE NEED INIT_REQUIRES (as a pickle)
    #     TODO:: Frozen tasks.. We need a way to kill them. start task work in a new process and kill it in case of emergency?
    #      we can just process ==> store PROCESSESS? done
    else:
        log.error(f"There are no such tasks supported by this Fuse.")
        log.error(f"Supported tasks: {task_type_from_db}")
#         TODO, how to report human mistake/errors?


# TODO : how about a check and retry at the end of the task execution in case for steps that did not fall into 'done' list
# TODO done list should be a file in case of emergency shut down
# TODO there should be a way to return 'error' in case some steps failed, but also return which steps succeeded and which didn't
# TODO LEARN and see if GEVENTS would be of good use
