import __init__
import pickle
from utils import logger_utils as log


def save_to_pickle(full_file_path, contents):
    try:
        with open(full_file_path, 'ab') as file:
            pickle.dump(contents, file)
        log.info(f"Succesfully written pickle at {full_file_path}")
    except Exception as e:
        log.exception(f"Something went wrong while trying to write into {full_file_path}")
        log.exception(e)


def read_from_pickle(full_file_path):
    try:
        with open(full_file_path, 'rb') as file:
            result = pickle.load(file)
            log.info(f"Succesfully read from {full_file_path}")
            return result
    except Exception as e:
        log.exception(f"Something went wrong while trying to read from {full_file_path}")
        log.exception(e)
