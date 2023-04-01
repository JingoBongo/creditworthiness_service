import __init__
import os
import time
from concurrent.futures import ProcessPoolExecutor
from zipfile import ZipFile
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from argparse import ArgumentParser
from utils import constants as c, os_utils, general_utils
from utils.flask_child import FuseNode
from utils.general_utils import init_start_function_thread


class ScreenshotHandler(FileSystemEventHandler):
    def __init__(self, source_folder, dest_folder):
        self.source_folder = source_folder
        self.dest_folder = dest_folder
        self.screenshots_list = []
        self.screenshotExecutor = ProcessPoolExecutor(max_workers=archiver_max_workers)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.png'):
            self.screenshots_list.append(event.src_path)
            if len(self.screenshots_list) >= 100:
                self.screenshotExecutor.submit(ScreenshotHandler.process_screenshots_list, self.screenshots_list.copy())
                self.screenshots_list.clear()

    @staticmethod
    def process_screenshots_list(local_screenshot_copy):
        screenshot_base = os.path.basename(local_screenshot_copy[0])
        zipp = ZipFile(f"{archives_folder_name}/{screenshot_base}.zip", 'w')
        app.logger.info(f"Archiving {screenshot_base} ++")
        for f in local_screenshot_copy:
            zipp.write(f)
            os.remove(f)
        zipp.close()
        app.logger.info(f"Finished archiving {screenshot_base} ++")


yt_dlp_used_playlists_file_path = c.temporary_files_folder_full_path + '//yt_dlp_used_playlists.txt'
videos_folder_name = c.temporary_files_folder_full_path + '//ytdlp_videos'
screenshots_folder_name = c.temporary_files_folder_full_path + '//ytlpd_screenshots'
archives_folder_name = c.temporary_files_folder_full_path + '//ytlpd_archives'
theshold_of_screenshots_to_panic = 10_000
archiver_max_workers = 2
parser = ArgumentParser()
app = FuseNode(__name__, arg_parser=parser)


def recreate_image_harvester_files_and_folders():
    if not os.path.exists(yt_dlp_used_playlists_file_path):
        open(yt_dlp_used_playlists_file_path, "w")
    if not os.path.exists(videos_folder_name):
        os.makedirs(videos_folder_name)
    if not os.path.exists(screenshots_folder_name):
        os.makedirs(screenshots_folder_name)
    if not os.path.exists(archives_folder_name):
        os.makedirs(archives_folder_name)


def process_existing_screenshots():
    app.logger.info(f"Processing existing screenshots")
    folder_path = screenshots_folder_name
    file_paths = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.png') and os.path.isfile(file_path):
            file_paths.append(file_path)

    for i, file_path in enumerate(file_paths):
        app.logger.info(
            f"Existing batch of screenshots No. {i}/{len(file_paths)} sent to screenshotExecutor Process Pool")
        event = FileCreatedEvent(file_path)
        screenshot_handler.on_created(event)
        if (i + 1) % theshold_of_screenshots_to_panic == 0:
            app.logger.warning(
                f"There is currently too big amount of screenshots ({len(file_paths)}), archiving is slowed down, "
                f"as well it is recommended to avoid sending requests to the module")
            time.sleep(180)


def watch_screenshot_folder():
    if os_utils.is_linux_running():
        from watchdog.observers.inotify import InotifyObserver
        observer = InotifyObserver()
    else:
        from watchdog.observers import Observer
        observer = Observer()
    observer.schedule(screenshot_handler, screenshots_folder_name, recursive=False)
    observer.start()
    init_start_function_thread(process_existing_screenshots)


def give_recreated_files_and_folders_permissions():
    # TODO NOTE if the problem persists with the files,
    # refer here to create folders/files already with needed permissions
    # https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python/67723702#67723702
    if os_utils.is_linux_running():
        # this might *need* sudo, even tho as service it is root already
        command = f"cd {c.temporary_files_folder_full_path} && chmod ugo+rwx *"
        general_utils.run_cmd_command_and_wait_response(command)


if __name__ == "__main__":
    recreate_image_harvester_files_and_folders()
    give_recreated_files_and_folders_permissions()
    screenshot_handler = ScreenshotHandler(screenshots_folder_name, archives_folder_name)
    init_start_function_thread(watch_screenshot_folder)
    app.run()
