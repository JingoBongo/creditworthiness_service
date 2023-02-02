import __init__

import json
from utils import logger_utils as log


def read_from_json(path: str):
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except Exception as e:
        log.exception(f'Something went horribly wrong when attempted to read from file "{path}"')
        log.exception(e)
        return {}


def write_to_json(path: str, text):
    try:
        with open(path, 'w') as outfile:
            json.dump(text, outfile)
    except Exception as e:
        log.exception(
            f'Something went horribly wrong when attempted to write into file "{path}" this specific text "{text}"')
        log.exception(e)
