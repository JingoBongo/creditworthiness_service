import __init__

from flask import render_template, redirect, url_for, request, Response
from utils import constants as c
from argparse import ArgumentParser
from utils import logger_utils as log
from utils.flask_child import FuseNode

parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)

# Idea behind this service. It is planned to be used like a worker; with the ability to start/stop/etc it from the web
# It is not going to have cron job, it is going to be launched as 1 file

# It will have 2-3 workers, 1st to collect screenshots in folders. 2nd to modify them to save space
# oooor mare those distinct services, because modularity, bitch!

# it will save images in temp folder, 500 in one folder?

# Folder will have generic name. RawImageFolder-{index}-{state}
# Where state can be {Empty}, {Ongoing}, {Complete}

# Somehow archive those folders? Transmitting 500 over the internet might be tricky


@app.route("/user/<string:str_variable>")
def endpoint_with_var(str_variable):
    """I have no idea why is this a title
        These are just notes as an example. We don't need most of this
        functionality, plus we aren't paid for this. So let's keep it
        simple as in hello_world endpoit, ey?
        ---
        parameters:
          - arg1: whatever, dude, this goes into business logic for now
            type: string
            required: true
            default: none, actually
        definitions:
          Job_id:
            type: String
        responses:
          200:
            description: A simple business logic unit with swagger
        """
    return 'elo hello fello\', %s' % str_variable


if __name__ == "__main__":
    app.run()




# import concurrent.futures
# import time
#
# def execute_task(role, task, args):
#     print(f'Actor with role "{role}" is executing task "{task}" with args "{args}"')
#     time.sleep(2)
#     print(f'Actor with role "{role}" finished executing task "{task}" with args "{args}"')
#
# def run_actors(role, task, args):
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_actor = {executor.submit(execute_task, role, task, args): role for role, task, args in zip(roles, tasks, args_list)}
#         for future in concurrent.futures.as_completed(future_to_actor):
#             actor = future_to_actor[future]
#             try:
#                 future.result()
#             except Exception as e:
#                 print(f'Actor with role "{actor}" generated an exception: {e}')
#
# roles = ['actor_1', 'actor_2', 'actor_3']
# tasks = ['task_1', 'task_2', 'task_3']
# args_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
#
# run_actors(roles, tasks, args_list)