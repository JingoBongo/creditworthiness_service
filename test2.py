import functools
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
from flask import Flask, jsonify
from utils import constants as c
from utils.flask_child import FuseNode


# Define worker names and statuses using enums
class WorkerName(Enum):
    DOWNLOADER = 'DOWNLOADER'
    SCREENSHOT_SPLITTER = 'SCREENSHOT_SPLITTER'
    SCREENSHOT_FILTERER = 'SCREENSHOT_FILTERER'
    SCREENSHOT_ARCHIVER = 'SCREENSHOT_ARCHIVER'

class WorkerStatus(Enum):
    IDLE = 'Idle'
    BUSY = 'Busy'


yt_dlp_used_playlists_file_path = c.temporary_files_folder_full_path + 'yt_dlp_used_playlists.txt'
videos_folder_name = c.temporary_files_folder_full_path + 'ytdlp_videos'
raw_screenshots_folder_name = c.temporary_files_folder_full_path + 'ytlpd_raw_screenshots'
filtered_screenshots_folder_name = c.temporary_files_folder_full_path + 'ytlpd_filtered_screenshots'

print('on top, before argparser')
parser = ArgumentParser()

# print('on top, before threadpool')
# threadpool = CustomThreadPool(num_threads=10)

print('on top, before fusenode')
app = FuseNode(__name__, arg_parser=parser)

# Create a dictionary to keep track of worker statuses
worker_status = {worker_name: WorkerStatus.IDLE for worker_name in WorkerName}

# Create a process pool executor with 4 workers
executor = ProcessPoolExecutor(max_workers=4)

# Define a task function that takes two arguments
def task(arg1, arg2):
    # do something with the arguments
    for i in range(5):
        print(i)
    return 'result'

# Define a Flask route that submits a task to the pool and updates the worker status
@app.route('/submit_task')
def submit_task():
    arg1 = 1
    arg2 = 2
    worker_name = WorkerName.DOWNLOADER
    worker_status[worker_name] = WorkerStatus.BUSY

    def on_finish(_fut, wworker_name):
        worker_status[wworker_name] = WorkerStatus.IDLE
    future = executor.submit(task, arg1, arg2)
    future.add_done_callback(functools.partial(on_finish, worker_name))
    # future.add_done_callback(on_finish(worker_name))
    # future.add_done_callback(lambda _: worker_status[worker_name] = WorkerStatus.IDLE)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run()