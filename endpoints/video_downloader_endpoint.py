import __init__
from flask import render_template, request, send_from_directory

import os
import re
from concurrent.futures import ProcessPoolExecutor
from argparse import ArgumentParser
from utils import constants as c, git_utils, yaml_utils, general_utils, os_utils

from utils.flask_child import FuseNode

yt_dlp_used_playlists_file_path = c.temporary_files_folder_full_path + '//yt_dlp_used_playlists.txt'
videos_folder_name = c.temporary_files_folder_full_path + '//ytdlp_videos'
screenshots_folder_name = c.temporary_files_folder_full_path + '//ytlpd_screenshots'
archives_folder_name = c.temporary_files_folder_full_path + '//ytlpd_archives'
parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)
downloadExecutor = ProcessPoolExecutor(max_workers=1)


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
    return [item.strip() for item in mylist]


def generate_bytesize_of_playlist(playlist_url):
    size_byte_res = general_utils.run_cmd_command_and_wait_response(
        f"yt-dlp --print \"%(filesize,filesize_approx)s\" -f \"bestvideo[height<=480]\" {playlist_url}")
    # 41788 bytes per second for 480p video, roughly
    # therefore length = ALL_BYTES / 156
    if type(size_byte_res) == bytes:
        if '\\n' in str(size_byte_res):  # then this is a list
            size_byte_res = sum(
                [int(el.decode('utf-8')) for el in size_byte_res.split() if re.match('^[0-9]+$', el.decode('utf-8'))])
        else:  # then this is a single video
            # TODO: I am not sure I didn't fuck this up, test on singular video
            size_byte_res = int(
                size_byte_res.decode('utf-8') if re.match('^[0-9]+$', size_byte_res.decode('utf-8')) else None)
        return size_byte_res
    else:
        return None


def make_sure_there_is_enough_space_for_playlist(dict_of_all_playlist_data):
    buffer_space = 20
    return os_utils.get_hard_drive_free_space_gbyte() > dict_of_all_playlist_data['size_gb'] + buffer_space


def download_videos_task_body(number_of_screenshots, list_of_playlists):
    app.logger.info(f"Started downloading")
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
        if make_sure_there_is_enough_space_for_playlist(local_dict):
            app.logger.info(
                f"{total_seconds_available=} is being complemented with {local_dict['duration_seconds']} seconds; "
                f"Downloading playlist {playlist}")
            download_playlist(playlist)
            append_new_used_playlists_to_file(playlist)

        else:
            app.logger.error(f"Not enough space ({os_utils.get_hard_drive_free_space_gbyte()} gbytes free) available")
            return
        if total_seconds_available >= number_of_screenshots:
            break
    app.logger.info(f"Stopped downloading")


def append_new_used_playlists_to_file(strings):
    strings = str(strings)
    filename = yt_dlp_used_playlists_file_path
    with open(filename, 'a') as f:
        if isinstance(strings, str):
            f.write(strings + '\n')
        elif isinstance(strings, list):
            for item in strings:
                f.write(item + '\n')
        else:
            raise TypeError("Data type not supported")


def download_playlist(playlist):
    app.logger.info(f"Starting downloading {playlist}")
    command = f"yt-dlp --verbose -ci -f \"bestvideo[height<=480]\" --geo-bypass -P \"{videos_folder_name}\" \"{playlist}\""
    return general_utils.run_cmd_command(command)


@app.route('/yt_downloader/show_archives')
def show_files():
    directory = archives_folder_name  # replace with your directory path
    files = os.listdir(directory)
    return render_template('file_list_explorer.html', files=files)


@app.route('/yt_downloader/download_files', methods=['POST'])
def download_files():
    directory = archives_folder_name  # replace with your directory path
    selected_files = request.form.getlist('files')

    # send each selected file as an attachment
    for filename in selected_files:
        # TODO: why is file_path needed?
        file_path = os.path.join(directory, filename)
        return send_from_directory(directory, filename, as_attachment=True)


# this todo is a big one: on linux machine it is needed to sudo chmod 755 ./fuse.py  ;
#  or permission denied will be a common thing

@app.route("/yt_downloader/how_many_screenshots_ready")
def show_ready_screenshot_count():
    for root, dirs, files in os.walk(archives_folder_name):
        return {'status': 'ok', 'amount': int(100 * len(files))}


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


@app.route("/yt_downloader/download/<int:number_of_screenshots>")
def download_videos(number_of_screenshots):
    list_of_playlists = git_utils.get_yaml_file_from_repository(yaml_utils.get_cloud_repo_from_config(),
                                                                'youtube_playlists.yaml')['list']
    if read_used_playlists_from_file() == list_of_playlists:
        return {'status': 'error', 'reason': 'all playlists from the file were already downloaded'}

    downloadExecutor.submit(download_videos_task_body, number_of_screenshots, list_of_playlists)

    return {'status': 'ok'}


if __name__ == "__main__":
    recreate_image_harvester_files_and_folders()
    app.run()
