import os
import queue

import __init__

from flask import render_template, redirect, url_for, request, Response
from utils import constants as c, general_utils, yaml_utils, git_utils, os_utils
from argparse import ArgumentParser
from utils import logger_utils as log
from utils.flask_child import FuseNode
import concurrent.futures
import time
import threading
from enum import Enum


# parser = ArgumentParser()
# app = FuseNode(__name__, arg_parser=parser)


# Idea behind this service. It is planned to be used like a worker; with the ability to start/stop/etc it from the web
# It is not going to have cron job, it is going to be launched as 1 file

# It will have 2-3 workers, 1st to collect screenshots in folders. 2nd to modify them to save space
# oooor mare those distinct services, because modularity, bitch!

# it will save images in temp folder, 500 in one folder?

# Folder will have generic name. RawImageFolder-{index}-{state}
# Where state can be {Empty}, {Ongoing}, {Complete}

# Somehow archive those folders? Transmitting 500 over the internet might be tricky

class WorkerName(Enum):
    DOWNLOADER = 'DOWNLOADER'
    SCREENSHOT_SPLITTER = 'SCREENSHOT_SPLITTER'
    SCREENSHOT_FILTERER = 'SCREENSHOT_FILTERER'
    SCREENSHOT_ARCHIVER = 'SCREENSHOT_ARCHIVER'


class WorkerStatus(Enum):
    IDLE = 'Idle'
    BUSY = 'Busy'
    ERROR = 'Error'


class Worker:
    def __init__(self):
        self.name = None
        self.status = WorkerStatus.IDLE


class CustomThreadPool:
    def __init__(self, num_threads):
        self.task_queue = queue.Queue()
        self.workers = [Worker() for _ in range(num_threads)]
        self.num_threads = num_threads
        self._start_workers()

    def _start_workers(self):
        for worker in self.workers:
            threading.Thread(target=self._run_worker, args=(worker,)).start()

    def _run_worker(self, worker):
        while True:
            task, args = self.task_queue.get()
            worker.status = WorkerStatus.BUSY
            try:
                task(worker.name, *args)
                worker.status = WorkerStatus.IDLE
            except Exception:
                worker.status = WorkerStatus.ERROR
            self.task_queue.task_done()

    def submit_task(self, task_func, wworker_name, *args):
        for worker in self.workers:
            if worker.name is None:
                worker.name = wworker_name
                task = (task_func, wworker_name, args)
                self.task_queue.put(task)
                worker.status = WorkerStatus.BUSY
                return
        raise ValueError("No available workers")

    def get_worker(self, wworker_name):
        for worker in self.workers:
            if worker.name == wworker_name:
                return worker
        raise ValueError(f"No worker with name {wworker_name} found")

    def get_worker_status(self, wworker_name) -> WorkerStatus:
        worker = self.get_worker(wworker_name)
        return worker.status

    def wait_completion(self):
        self.task_queue.join()


yt_dlp_used_playlists_file_path = c.temporary_files_folder_full_path + 'yt_dlp_used_playlists.txt'
videos_folder_name = c.temporary_files_folder_full_path + 'ytdlp_videos'
raw_screenshots_folder_name = c.temporary_files_folder_full_path + 'ytlpd_raw_screenshots'
filtered_screenshots_folder_name = c.temporary_files_folder_full_path + 'ytlpd_filtered_screenshots'

print('on top, before argparser')
parser = ArgumentParser()

print('on top, before threadpool')
threadpool = CustomThreadPool(num_threads=10)

print('on top, before fusenode')
app = FuseNode(__name__, arg_parser=parser)



# parser = ArgumentParser()
# app = FuseNode2(__name__, arg_parser=parser)


# Idea behind this service. It is planned to be used like a worker; with the ability to start/stop/etc it from the web
# It is not going to have cron job, it is going to be launched as 1 file

# It will have 2-3 workers, 1st to collect screenshots in folders. 2nd to modify them to save space
# oooor mare those distinct services, because modularity, bitch!

# it will save images in temp folder, 500 in one folder?

# Folder will have generic name. RawImageFolder-{index}-{state}
# Where state can be {Empty}, {Ongoing}, {Complete}

# Somehow archive those folders? Transmitting 500 over the internet might be tricky


def download_playlist(playlist):
    command = f"yt-dlp --verbose -ci -f \"bestvideo[height<=480]\" --geo-bypass -P \"{videos_folder_name}\" \"{playlist}\""
    return general_utils.run_cmd_command(command)


def make_sure_there_is_enough_space_for_videos(dict_of_all_playlists, list_of_chosen_playlists):
    total_memory_to_be_used = 0
    for el in dict_of_all_playlists.values():
        if el['url'] in list_of_chosen_playlists:
            total_memory_to_be_used += el['size_gb']
    return os_utils.get_hard_drive_free_space_gbyte() < total_memory_to_be_used


def downloader_thread_is_currently_working():
    for worker in threadpool.workers:
        status = threadpool.get_worker_status(worker.name)
        if WorkerStatus.BUSY == status:
            return True
    return False


def recreate_image_harvester_files_and_folders():
    if not os.path.exists(yt_dlp_used_playlists_file_path):
        open(yt_dlp_used_playlists_file_path, "w")
    if not os.path.exists(videos_folder_name):
        os.makedirs(videos_folder_name)
    if not os.path.exists(raw_screenshots_folder_name):
        os.makedirs(raw_screenshots_folder_name)
    if not os.path.exists(filtered_screenshots_folder_name):
        os.makedirs(filtered_screenshots_folder_name)


def read_used_playlists_from_file():
    with open(yt_dlp_used_playlists_file_path, 'r') as f:
        mylist = f.readlines()
    # Remove newline characters from each string in the list
    return [item.strip() for item in mylist]


# def write_new_used_play
def append_new_used_playlists_to_file(*strings):
    filename = yt_dlp_used_playlists_file_path
    with open(filename, 'w') as f:
        if isinstance(strings[0], str):
            f.write(strings[0])
        else:
            for string in strings[0]:
                f.write(string + '\n')


@app.route("/yt_downloader/worker_statuses")
def return_worker_statuses():
    workers_and_statuses = {}
    for worker in threadpool.workers:
        workers_and_statuses[worker.name] = worker.status
    return workers_and_statuses


@app.route("/yt_downloader/download/<int:number_of_screenshots>")
def download_videos(number_of_screenshots):
    if downloader_thread_is_currently_working():
        return {'status': 'error', 'reason': 'download worker currently busy'}

    # the idea is that the list of videos can be taken from source X, say, a repo.
    # So, let's leave a list of playlists in a repo...
    # number of screenshots roughly matches number of second that the videos have
    list_of_playlists = git_utils.get_yaml_file_from_repository(yaml_utils.get_cloud_repo_from_config(),
                                                                'youtube_playlists.yaml')['list']
    if read_used_playlists_from_file() == list_of_playlists:
        return {'status': 'error', 'reason': 'all playlists from the file were already downloaded'}

    dict_of_playlists_with_data = {}
    for playlist in list_of_playlists:
        # TODO: add internal list of all already used playlists, they are added in that list in the moment download
        if playlist in read_used_playlists_from_file():
            continue
        # by their link is started. they are ignored here
        # if already used => break

        #   well, first we need length and size of each element of each playlist.. or just for playlists

        size_byte_res = general_utils.run_cmd_command_and_wait_response(
            f"yt-dlp --print \"%(filesize,filesize_approx)s\" -f \"bestvideo[height<=480]\" {playlist}")
        # 41788 bytes per second for 480p video, roughly
        # therefore length = ALL_BYTES / 156
        # dict_of_playlists_with_data[playlist] = {}
        if '\\n' in str(size_byte_res):  # then this is a list
            size_byte_res = sum([int(el.decode('utf-8')) for el in size_byte_res.split()])
        else:  # then this is a single video
            size_byte_res = int(size_byte_res.decode('utf-8'))

        local_dict = {'size_b': size_byte_res,
                      'size_gb': size_byte_res / c.one_thousand_to_the_power_3,
                      'url': playlist,
                      'duration_seconds': int(size_byte_res / 41788)}
        dict_of_playlists_with_data[playlist] = local_dict
        # here we should theoretically have all data about playlists
    total_seconds_available = 0
    playlists_to_download_list = []
    for playlist_dict in dict_of_playlists_with_data.values():
        temp_seconds = playlist_dict['duration_seconds']
        playlists_to_download_list.append(playlist_dict['url'])
        if total_seconds_available + temp_seconds > number_of_screenshots:
            break
        total_seconds_available += temp_seconds


    if make_sure_there_is_enough_space_for_videos(dict_of_playlists_with_data, playlists_to_download_list):
        # TODO add playlists from playlists_to_download_list somewhere as already used
        # Do I do it here properly or do i entirely rely on making this module standalone?
        # for now: standalone. therefore create needed file in resources
        # TODO: at the start of module create needed files, folders
        append_new_used_playlists_to_file(playlists_to_download_list)
        for playlist in playlists_to_download_list:
            threadpool.submit_task(download_playlist, WorkerName.DOWNLOADER, playlist)
        return {'status': 'ok'}
    return {'status': 'error', 'reason': 'not enough space for such number of videos'}


@app.route("/endpoint_with_varuser/<string:str_variable>")
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


# @app.route("/yt_downloader/download/<intLnumber_of>")

if __name__ == "__main__":
    print('in main, before recreate folders')
    recreate_image_harvester_files_and_folders()

    print('in main, before app run')
    app.run()
