import os
import re
import signal
import subprocess
import threading
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import cv2
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from utils import constants as c, os_utils
from utils.dataclasses.thread_with_return_value import ThreadWithReturnValue


class FaceCutterHandler(FileSystemEventHandler):
    def __init__(self):
        self.compressorExecutor = ProcessPoolExecutor(max_workers=compresser_max_workers)

    def on_created(self, event):
        if not event.is_directory:
            self.compressorExecutor.submit(process_one_zip, event.src_path)



face_cascade = cv2.CascadeClassifier("resources/lbpcascade_frontalface.xml")
pattern = r'[^a-zA-Z0-9\s]'
replace = ''


archives_folder_name = c.temporary_files_folder_full_path + '//ytlpd_archives'
compressed_folder_name = c.temporary_files_folder_full_path + '//ytlpd_compressed_archives'
theshold_of_archives_to_panic = 200
compresser_max_workers = 1


def init_start_function_thread(function, *argss, **kwargss) -> ThreadWithReturnValue:
    thread: ThreadWithReturnValue = ThreadWithReturnValue(target=function, args=argss, kwargs=kwargss)
    thread.start()
    print(f"Created thread for function {function.__name__} with args {argss} and kwargs {kwargss}")
    return thread

def get_files_from_zip(zip_file_path):
    files = {}
    offset = 0.05
    with zipfile.ZipFile(zip_file_path, 'r') as archive:
        for item in archive.infolist():
            if not item.is_dir():
                file_name = os.path.basename(item.filename)
                file_name = re.sub(pattern, replace, file_name)
                file_contents = archive.read(item.filename)
                # ML part
                input_img = cv2.imdecode(np.frombuffer(file_contents, np.uint8), cv2.IMREAD_COLOR)

                if input_img.shape[2] == 1:
                    input_img = cv2.cvtColor(input_img, cv2.COLOR_GRAY2RGB)
                elif input_img.shape[2] == 3 and input_img.ndim == 2:
                    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)

                faces = face_cascade.detectMultiScale(input_img, scaleFactor=1.1, minNeighbors=10)

                # Loop over the detected faces and extract them
                i = 0
                for (x, y, w, h) in faces:
                    #   considering found face, apply offset to save some additional face elements
                    x_offset, y_offset = int(w * offset), int(h * offset)

                    #   considering face start point, its width and height, offsets to apply -
                    # calculate start point, end point and make sure that it's not going out
                    # of the image size
                    x = x - x_offset if x_offset < x else 0
                    y = y - y_offset if y_offset < y else 0
                    x_end = x + w + 2 * x_offset
                    y_end = y + h + 2 * y_offset
                    x_end = x_end if x_end < input_img.shape[1] else input_img.shape[1]
                    y_end = y_end if y_end < input_img.shape[0] else input_img.shape[0]
                    # Crop the face region from the image
                    face = input_img[y:y_end, x:x_end]
                    face_img = np.array(face)
                    files[f"{file_name[:-3]}_{i}.jpg"] = face_img
                    i += 1


    return files

def process_one_zip(zip_path):
    basename = os.path.basename(zip_path)
    print(f"Compressing {basename}")
    new_zip_path = f"{compressed_folder_name}//{basename}"
    source_files = get_files_from_zip(zip_path)
    os.remove(zip_path)
    with zipfile.ZipFile(new_zip_path, 'w') as archive:
        for file_name, img_array in source_files.items():
            img_buffer = cv2.imencode('.jpg', img_array)[1].tobytes()
            archive.writestr(file_name, img_buffer)
    print(f"Finished compressing {basename}")


def signal_handler(signum, frame):
    """
    Signal handler that terminates all subprocesses and threads.
    """
    os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
    threading.Timer(5, os.kill, args=(os.getpid(), signal.SIGKILL)).start()



def give_recreated_files_and_folders_permissions():
    # TODO NOTE if the problem persists with the files,
    # refer here to create folders/files already with needed permissions
    # https://stackoverflow.com/questions/5231901/permission-problems-when-creating-a-dir-with-os-makedirs-in-python/67723702#67723702
    if os_utils.is_linux_running():
        # this might *need* sudo, even tho as service it is root already
        command = f"cd {c.temporary_files_folder_full_path} && chmod ugo+rwx *"
        run_cmd_command_and_wait_response(command)


def run_cmd_command_and_wait_response(command):
    print(f'triggering command :{command}')
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output = proc.stdout.read()

    print(f"{run_cmd_command_and_wait_response.__name__} executed '{command}' and returned value: {output}")
    return output

def watch_archives_folder():
    if os_utils.is_linux_running():
        from watchdog.observers.inotify import InotifyObserver
        observer = InotifyObserver()
    else:
        from watchdog.observers import Observer
        observer = Observer()
    observer.schedule(compressor_handler, archives_folder_name, recursive=False)
    observer.start()
    init_start_function_thread(process_existing_archives)

def process_existing_archives():
    print(f"Processing existing archives")
    existing_files = []
    for filename in os.listdir(archives_folder_name):
        file_path = os.path.join(archives_folder_name, filename)
        if os.path.isfile(file_path):
            existing_files.append(file_path)
    amount_of_archives = len(existing_files)
    ind = 0
    for existing_file in existing_files:
        print(f"Existing archive No. {ind}/{amount_of_archives} sent to archiveExecutor Process Pool")
        event = FileCreatedEvent(existing_file)
        compressor_handler.on_created(event)
        ind += 1
        if ind % theshold_of_archives_to_panic == 0:
            print(
                f"There is currently too big amount of archives ({len(existing_files)}), compressing is slowed down")
            time.sleep(100)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if not os.path.exists(compressed_folder_name):
        os.makedirs(compressed_folder_name)
    give_recreated_files_and_folders_permissions()
    compressor_handler = FaceCutterHandler()
    init_start_function_thread(watch_archives_folder)

    while True:
        pass