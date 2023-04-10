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



face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
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
    # offset = 0.2
    with zipfile.ZipFile(zip_file_path, 'r') as archive:
    # archive = zipfile.ZipFile(zip_file_path, 'r')
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

                faces = face_cascade.detectMultiScale(input_img, scaleFactor=1.1, minNeighbors=5)

                # Loop over the detected faces and extract them
                i = 0
                for (x, y, w, h) in faces:
                    # Crop the face region from the image
                    face = input_img[y:y + h, x:x + w]
                    face_img = np.array(face)
                    files[f"{file_name[:-3]}_{i}.jpg"] = face_img
                    i += 1

    return files


def crop_faces_in_zip(input_zip_path, output_zip_path):
    """
    Detects faces in all images in a zip file and crops them based on the detected faces, then saves them to a new zip file.

    Args:
        input_zip_path (str): The path to the input zip file.
        output_zip_path (str): The path to the output zip file.
    """

    # print(f"1 {os.path.normpath(input_zip_path)=}")
    with zipfile.ZipFile(os.path.normpath(input_zip_path) , 'r') as input_zip :
        # print(f"2 {os.path.normpath(output_zip_path)=}")
        with zipfile.ZipFile(os.path.normpath(output_zip_path) , 'w', zipfile.ZIP_DEFLATED) as output_zip :
            # print("3")
            for name in input_zip.namelist():
                # print("4")
                if not '.jpg' in name or not '.png' in name:
                    continue
                input_file = input_zip.open(name)
                # print("5")
                np_img = np.frombuffer(input_file.read(), np.uint8)
                # print("6")
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                # print("7")
                if img.shape[2] == 1:
                    # print("8")
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                    # print("9")
                elif img.shape[2] == 3 and img.ndim == 2:
                    # print("10")
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    # print("11")
                # print("12")
                faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))
                # print("13")
                i = 0
                for (x, y, w, h) in faces:
                    # print("14")
                    # Crop the face region from the image
                    face = img[y:y + h, x:x + w]
                    face_img = np.array(face)
                    # print("15")
                    success, buffer = cv2.imencode('.jpg', face_img)
                    # print("16")
                    parts = os.path.basename(name).split('.')
                    # print("17")
                    output_zip.writestr(f"{'.'.join(parts[:-1])}_{i}.jpg", buffer)
                    # print("18")
                    i += 1
    # os.remove()



def process_one_zip(zip_path):
    basename = os.path.basename(zip_path)
    print(f"Compressing {basename}")
    new_zip_path = f"{compressed_folder_name}//{basename}"
    crop_faces_in_zip(zip_path, new_zip_path)
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
