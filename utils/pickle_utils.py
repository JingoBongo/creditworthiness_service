import __init__
import pickle
from utils import logger_utils as log


def save_to_pickle(full_file_path: str, contents):
    """
    save given content into pickle file

    Args:
        full_file_path (str): path to file where pickle object will be saved
        contents (obj): any data
    """
    try:
        with open(full_file_path, 'ab') as file:
            pickle.dump(contents, file)
        log.debug(f"Successfully written pickle at {full_file_path}")
    except Exception as e:
        log.exception(f"Something went wrong while trying to write into {full_file_path}")
        log.exception(e)


def read_from_pickle(full_file_path: str):
    """
    get object out of pickle file

    Args:
        full_file_path (str): path to file where pickle is located

    Returns:
        object obtained out of pickle read
    """
    try:
        with open(full_file_path, 'rb') as file:
            result = pickle.load(file)
            log.debug(f"Successfully read from {full_file_path}")
            return result
    except Exception as e:
        log.exception(f"Something went wrong while trying to read from {full_file_path}")
        log.exception(e)
