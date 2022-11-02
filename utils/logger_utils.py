import __init__
from logging.handlers import RotatingFileHandler
import os
import sys

import logging
from utils import constants as c
from utils.config_utils import getDebugFlagFromConfig


def setup_logger(name, log_file, level=logging.INFO):
    # level = (logging.INFO ? not getDebugFlagFromConfig() : logging.DEBUG)
    # level = (bool(getDebugFlagFromConfig()) ? logging.DEBUG : logging.INFO)
    level = logging.DEBUG if getDebugFlagFromConfig() else logging.INFO
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

    # log_formatter = logging.Formatter("[%(asctime)s] [%(name)-s] [%(filename)s] [%(levelname)-s] %(message)s")
    log_formatter = logging.Formatter("[%(asctime)s] [%(name)-s] [%(levelname)-s] %(message)s")
    # handler = logging.FileHandler(log_file)
    handler = RotatingFileHandler(log_file, maxBytes=50 * 1024, backupCount=2)
    handler.setFormatter(log_formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.emit = decorate_emit(console_handler.emit)

    c.current_rotating_handler = handler
    c.current_console_handler = console_handler
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger


def get_log(name):
    pid = os.getpid()
    logger_name = f"{name}-{pid}"
    log_path = f"{c.root_path}resources//{c.logs_folder_name}//{logger_name}"
    log = setup_logger(logger_name, log_path)
    c.current_subprocess_logger = log
    sys.excepthook = handle_exception
    return log


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    c.current_subprocess_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def info(text):
    c.current_subprocess_logger.info(text)


def debug(text):
    c.current_subprocess_logger.debug(text)


def error(text):
    c.current_subprocess_logger.error(text)


def warn(text):
    c.current_subprocess_logger.warn(text)


def critical(text):
    c.current_subprocess_logger.critical(text)


def exception(text):
    c.current_subprocess_logger.exception(text)
