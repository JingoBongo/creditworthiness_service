import __init__
import os
import sys

import logging
from utils import constants as c



def setup_logger(name, log_file, level=logging.INFO):

    def decorate_emit(fn):
        def new(*args):
            levelno = args[0].levelno
            if levelno >= logging.CRITICAL:
                color = '\x1b[31;1m'
            elif levelno >= logging.ERROR:
                color = '\x1b[31;1m'
            elif levelno >= logging.WARNING:
                color = '\x1b[33;1m'
            elif levelno >= logging.INFO:
                color = '\x1b[32;1m'
            elif levelno >= logging.DEBUG:
                color = '\x1b[35;1m'
            else:
                color = '\x1b[0m'
            # add colored *** in the beginning of the message
            args[0].msg = "{0}***\x1b[0m {1}".format(color, args[0].msg)

            # new feature i like: bolder each args of message
            args[0].args = tuple('\x1b[1m' + arg + '\x1b[0m' for arg in args[0].args)
            return fn(*args)
        return new

    """To setup as many loggers as you want"""
    logFormatter = logging.Formatter("[%(asctime)s] [%(name)-s] [%(levelname)-s] %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logFormatter)
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.emit = decorate_emit(consoleHandler.emit)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(consoleHandler)

    return logger


def get_log(name):
    pid = os.getpid()
    logger_name = f"{name}-{pid}"
    log_path = f"{c.root_path}resources//{c.logs_folder_name}//{logger_name}"
    log = setup_logger(logger_name, log_path)
    c.current_subprocess_logger = log
    return log