# import os
# import time
# from argparse import ArgumentParser
# from concurrent.futures import ProcessPoolExecutor
# from threading import Thread
#
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from flask import Flask, request
# from utils import logger_utils as log
#
# from utils.flask_child import FuseNode
#
# parser = ArgumentParser()
# # app = Flask(__name__)
# app = FuseNode(__name__, arg_parser=parser)
# executor = ProcessPoolExecutor()
#
# class MyHandler(FileSystemEventHandler):
#     def on_created(self, event):
#         if not event.is_directory:
#             print("New file created: ", event.src_path)
#             # Submit task to pool
#             executor.submit(task, event.src_path)
#
# def task(file_path):
#     # Task to be executed by the pool
#     app.logger.info(f"Processing file:  {file_path}")
#     time.sleep(1)
#     app.logger.info(f"File processing completed: {file_path}")
#
# def thread_body():
#     executor.submit(task, 'aboba in thread')
#
# @app.route('/submit_task')
# def submit_task():
#     # Submit task to pool
#     # executor.submit(task, 'aboba')
#     t = Thread(target=thread_body)
#     t.start()
#     return 'Task submitted'
#
# if __name__ == "__main__":
#     # Watchdog to monitor the directory for new files
#     # t = Thread(target=thread_body)
#     # t.start()
#     thread_body()
#     event_handler = MyHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path='D:\Files\PyProjects\\resources\\temporary_files\ytlpd_archives', recursive=False)
#     observer.start()
#
#     # Run the Flask app
#     app.run()