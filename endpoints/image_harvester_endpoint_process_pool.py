import re
import zipfile

from flask import request, send_from_directory, render_template

import __init__
from zipfile import ZipFile
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from utils import constants as c, general_utils, yaml_utils, git_utils, os_utils
from argparse import ArgumentParser
from utils import logger_utils as log
from utils.flask_child import FuseNode
import cv2
from enum import Enum

from utils.general_utils import init_start_function_thread


class WorkerName(Enum):
    DOWNLOADER = 'DOWNLOADER'
    SCREENSHOT_SPLITTER = 'SCREENSHOT_SPLITTER'
    SCREENSHOT_FILTERER = 'SCREENSHOT_FILTERER'
    SCREENSHOT_ARCHIVER = 'SCREENSHOT_ARCHIVER'


class WorkerStatus(Enum):
    IDLE = 'Idle'
    BUSY = 'Busy'
    ERROR = 'Error'


yt_dlp_used_playlists_file_path = c.temporary_files_folder_full_path + '//yt_dlp_used_playlists.txt'
videos_folder_name = c.temporary_files_folder_full_path + '//ytdlp_videos'
screenshots_folder_name = c.temporary_files_folder_full_path + '//ytlpd_screenshots'
archives_folder_name = c.temporary_files_folder_full_path + '//ytlpd_archives'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

parser = ArgumentParser()

app = FuseNode(__name__, arg_parser=parser)

worker_statuses = {worker_name: WorkerStatus.IDLE for worker_name in WorkerName}
executor = ProcessPoolExecutor(max_workers=2)


def download_playlist(playlist):
    log.info(f"Starting downloading {playlist}")
    command = f"yt-dlp --verbose -ci -f \"bestvideo[height<=480]\" --geo-bypass -P \"{videos_folder_name}\" \"{playlist}\""
    return general_utils.run_cmd_command(command)


def make_sure_there_is_enough_space_for_videos(dict_of_all_playlists, list_of_chosen_playlists):
    total_memory_to_be_used = 0
    for el in dict_of_all_playlists.values():
        if el['url'] in list_of_chosen_playlists:
            total_memory_to_be_used += el['size_gb']
    buffer_space = 20
    return os_utils.get_hard_drive_free_space_gbyte() + buffer_space > total_memory_to_be_used


def make_sure_there_is_enough_space_for_video(dict_of_all_playlist):
    buffer_space = 20
    return os_utils.get_hard_drive_free_space_gbyte() + buffer_space > dict_of_all_playlist['size_gb']


def downloader_thread_is_currently_working():
    return worker_statuses[WorkerName.DOWNLOADER] == WorkerStatus.BUSY


def recreate_image_harvester_files_and_folders():
    if not os.path.exists(yt_dlp_used_playlists_file_path):
        open(yt_dlp_used_playlists_file_path, "w")
    if not os.path.exists(videos_folder_name):
        os.makedirs(videos_folder_name)
    if not os.path.exists(screenshots_folder_name):
        os.makedirs(screenshots_folder_name)
    if not os.path.exists(archives_folder_name):
        os.makedirs(archives_folder_name)


def read_used_playlists_from_file():
    with open(yt_dlp_used_playlists_file_path, 'r') as f:
        mylist = f.readlines()
    # Remove newline characters from each string in the list
    return [item.strip() for item in mylist]


# def write_new_used_play
def append_new_used_playlists_to_file(*strings):
    filename = yt_dlp_used_playlists_file_path
    with open(filename, 'a') as f:
        if isinstance(strings[0], str):
            f.write(strings[0])
        else:
            for string in strings[0]:
                f.write(string + '\n')


@app.route("/yt_downloader/worker_statuses")
def return_worker_statuses():
    li = []
    for key, value in worker_statuses.items():
        li.append({key.value: value.value})
    return str(li)


def generate_bytesize_of_playlist(playlist_url):
    size_byte_res = general_utils.run_cmd_command_and_wait_response(
        f"yt-dlp --print \"%(filesize,filesize_approx)s\" -f \"bestvideo[height<=480]\" {playlist_url}")
    # 41788 bytes per second for 480p video, roughly
    # therefore length = ALL_BYTES / 156
    # dict_of_playlists_with_data[playlist] = {}
    if type(size_byte_res) == bytes:
        if '\\n' in str(size_byte_res):  # then this is a list
            size_byte_res = sum(
                [int(el.decode('utf-8')) for el in size_byte_res.split() if re.match('^[0-9]+$', el.decode('utf-8'))])
        else:  # then this is a single video
            # TODO: I am not sure I didn't fuck this up, test on singular video
            size_byte_res = int(
                s := size_byte_res.decode('utf-8') if re.match('^[0-9]+$', size_byte_res.decode('utf-8')) else None)
        return size_byte_res
    else:
        return None


def cut_and_archive():
    cut_videos_into_raw_screenshots()
    archive_filtered_screenshots()


@app.route("/yt_downloader/cut_and_archive")
def cut_and_archive_videos():
    init_start_function_thread(cut_and_archive)
    return {'status': 'ok'}


@app.route("/yt_downloader/get_approximation_of_available_screenshots")
def get_available_screenshot_approx():
    list_of_playlists = git_utils.get_yaml_file_from_repository(yaml_utils.get_cloud_repo_from_config(),
                                                                'youtube_playlists.yaml')['list']
    dict_of_playlists_with_data = {}
    total_seconds_available = 0
    playlists_to_download_list = []
    for playlist in list_of_playlists:
        if playlist in read_used_playlists_from_file():
            continue
        #   well, first we need length and size of each element of each playlist.. or just for playlists

        # this function is pretty slow. it is slower the more videos are there in the playlist, no way to speed up
        size_byte_res = generate_bytesize_of_playlist(playlist)

        local_dict = {'size_b': size_byte_res,
                      'size_gb': size_byte_res / c.one_thousand_to_the_power_3,
                      'url': playlist,
                      'duration_seconds': int(size_byte_res / 41788)}
        dict_of_playlists_with_data[playlist] = local_dict
        # here we should theoretically have all data about playlists
        total_seconds_available += local_dict['duration_seconds']
        playlists_to_download_list.append(local_dict['url'])
    print(str({'num_of_playlists': len(playlists_to_download_list),
               'approximate_screenshot_amount': total_seconds_available}))
    return {'num_of_playlists': len(playlists_to_download_list),
            'approximate_screenshot_amount': total_seconds_available}


@app.route('/yt_downloader/show_archives')
def show_files():
    directory = archives_folder_name  # replace with your directory path
    files = os.listdir(directory)
    return render_template('file_list_explorer.html', files=files)


@app.route("/yt_downloader/clear_errored_videos")
def clear_errored_videos():
    for root, dirs, files in os.walk(videos_folder_name):
        for file in files:
            file_full_path = os.path.join(root, file)
            if not file.endswith(".webm"):
                os.remove(file_full_path)
    return {'status': 'ok'}


@app.route("/yt_downloader/clear_webm_videos")
def clear_webm_videos():
    for root, dirs, files in os.walk(videos_folder_name):
        for file in files:
            file_full_path = os.path.join(root, file)
            if file.endswith(".webm"):
                os.remove(file_full_path)
    return {'status': 'ok'}


@app.route("/yt_downloader/how_many_screenshots_ready")
def show_ready_screenshot_count():
    for root, dirs, files in os.walk(archives_folder_name):
        return {'status': 'ok', 'amount': int(100 * len(files))}


@app.route('/yt_downloader/download', methods=['POST'])
def download_files():
    directory = archives_folder_name  # replace with your directory path
    selected_files = request.form.getlist('files')

    # send each selected file as an attachment
    for filename in selected_files:
        file_path = os.path.join(directory, filename)
        return send_from_directory(directory, filename, as_attachment=True)


# this todo is a big one: on linux machine it is needed to sudo chmod 755 ./fuse.py  ;
#  or permission denied will be a common thing


def download_two_endpoint_body(number_of_screenshots, list_of_playlists):
    total_seconds_available = 0
    for playlist in list_of_playlists:
        if playlist in read_used_playlists_from_file():
            continue

        size_byte_res = generate_bytesize_of_playlist(playlist)
        local_dict = {'size_b': size_byte_res,
                      'size_gb': size_byte_res / c.one_thousand_to_the_power_3,
                      'url': playlist,
                      'duration_seconds': int(size_byte_res / 41788)}

        total_seconds_available += local_dict['duration_seconds']
        if make_sure_there_is_enough_space_for_video(local_dict):
            download_one_playlist_function_body(playlist)
        else:
            return
        if total_seconds_available >= number_of_screenshots:
            break
    cut_videos_into_raw_screenshots()
    archive_filtered_screenshots()


@app.route("/yt_downloader/download2/<int:number_of_screenshots>")
def download_videos2(number_of_screenshots):
    if downloader_thread_is_currently_working():
        return {'status': 'error', 'reason': 'download worker currently busy'}

    # the idea is that the list of videos can be taken from source X, say, a repo.
    # So, let's leave a list of playlists in a repo...
    # number of screenshots roughly matches number of second that the videos have
    list_of_playlists = git_utils.get_yaml_file_from_repository(yaml_utils.get_cloud_repo_from_config(),
                                                                'youtube_playlists.yaml')['list']
    if read_used_playlists_from_file() == list_of_playlists:
        return {'status': 'error', 'reason': 'all playlists from the file were already downloaded'}
    init_start_function_thread(download_two_endpoint_body, number_of_screenshots, list_of_playlists)

    return {'status': 'ok'}


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
    total_seconds_available = 0
    playlists_to_download_list = []
    for playlist in list_of_playlists:
        if playlist in read_used_playlists_from_file():
            continue
        #   well, first we need length and size of each element of each playlist.. or just for playlists

        # this function is pretty slow. it is slower the more videos are there in the playlist, no way to speed up
        size_byte_res = generate_bytesize_of_playlist(playlist)

        local_dict = {'size_b': size_byte_res,
                      'size_gb': size_byte_res / c.one_thousand_to_the_power_3,
                      'url': playlist,
                      'duration_seconds': int(size_byte_res / 41788)}
        dict_of_playlists_with_data[playlist] = local_dict
        # here we should theoretically have all data about playlists
        total_seconds_available += local_dict['duration_seconds']
        playlists_to_download_list.append(local_dict['url'])
        if total_seconds_available >= number_of_screenshots:
            break

    if total_seconds_available < number_of_screenshots:
        return {'status': 'error',
                'reason': f"There are only {total_seconds_available} screenshots to download, when "
                          f"{number_of_screenshots} were asked. You might want to add new items to the list of "
                          f"playlists here: {yaml_utils.get_cloud_repo_from_config()}/youtube_playlists.yaml"}

    if make_sure_there_is_enough_space_for_videos(dict_of_playlists_with_data, playlists_to_download_list):
        init_start_function_thread(download_playlists_function_body, playlists_to_download_list)
        return {'status': 'ok'}
    return {'status': 'error', 'reason': 'not enough space for such number of videos'}


def download_playlists_function_body(playlists_to_download_list):
    worker_statuses[WorkerName.DOWNLOADER] = WorkerStatus.BUSY
    # TODO add playlists from playlists_to_download_list somewhere as already used
    # Do I do it here properly or do i entirely rely on making this module standalone?
    # for now: standalone. therefore create needed file in resources
    # TODO: at the start of module create needed files, folders

    # doing below line one by one is safer, even though a bit slower and splitted into multiple operations
    # append_new_used_playlists_to_file(playlists_to_download_list)

    for playlist in playlists_to_download_list:
        future = executor.submit(download_playlist, playlist)
        result = future.result()
        append_new_used_playlists_to_file(playlist)
    #     all necessary downloads are made, start a function to cut screenshots
    worker_statuses[WorkerName.DOWNLOADER] = WorkerStatus.IDLE
    cut_videos_into_raw_screenshots()
    clear_webm_videos()
    archive_filtered_screenshots()


def download_one_playlist_function_body(playlist_to_download):
    worker_statuses[WorkerName.DOWNLOADER] = WorkerStatus.BUSY
    # TODO add playlists from playlists_to_download_list somewhere as already used
    # Do I do it here properly or do i entirely rely on making this module standalone?
    # for now: standalone. therefore create needed file in resources
    # TODO: at the start of module create needed files, folders

    # doing below line one by one is safer, even though a bit slower and splitted into multiple operations
    # append_new_used_playlists_to_file(playlists_to_download_list)

    future = executor.submit(download_playlist, playlist_to_download)
    result = future.result()
    append_new_used_playlists_to_file(playlist_to_download)
    #     all necessary downloads are made, start a function to cut screenshots
    worker_statuses[WorkerName.DOWNLOADER] = WorkerStatus.IDLE
    # init_start_function_thread(cut_and_archive)
    # cut_videos_into_raw_screenshots()
    # archive_filtered_screenshots()


def archive_filtered_screenshots():
    for root, dirs, files in os.walk(screenshots_folder_name):
        ind = 0
        files_to_zip = []
        for file in files:
            file_full_path = os.path.join(root, file)
            screenshot_base = os.path.basename(file)

            if file.endswith(".png"):
                files_to_zip.append(file_full_path)
                if ind == 100:
                    with ZipFile(f"{archives_folder_name}/{screenshot_base}.zip", 'w') as zipObj:
                        print(f" Archiving {screenshot_base}")
                        [zipObj.write(f) for f in files_to_zip]
                        [os.remove(f) for f in files_to_zip]
                        ind = 0
                        files_to_zip.clear()
                ind += 1


def cut_one_video_into_screenshots(video_path):
    video_base = os.path.basename(video_path)
    print(f" Working on {video_base} cutting to screenshots")
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    index = 0
    i = 1
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if i % fps == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0:
                cv2.imwrite(f"{screenshots_folder_name}/{video_base}_{str(index)}.png", frame)
                index += 1
        i += 1

    cap.release()
    if os.path.exists(video_path):
        os.remove(video_path)



def cut_videos_into_raw_screenshots():
    threadpool = ThreadPoolExecutor(max_workers=3)
    for root, dirs, files in os.walk(videos_folder_name):
        for file in files:
            file_full_path = os.path.join(root, file)
            if file.endswith(".webm"):
                threadpool.submit(cut_one_video_into_screenshots, file_full_path)
    threadpool.shutdown(wait=True)


# @app.route("/yt_downloader/download/<intLnumber_of>")

if __name__ == "__main__":
    recreate_image_harvester_files_and_folders()
    app.run()

# TODO: add checks before making screenshots and archives to check if there is at least.. 20 gigs of space
