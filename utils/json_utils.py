import json
import os

cur_file_name = os.path.basename(__file__)


def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def read_from_json(path):
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except Exception as e:
        print_c(f'Something went horribly wrong when attempted to read from file "{path}"')
        print_c(e)
        return {}


def write_to_json(path, text):
    try:
        with open(path, 'w') as outfile:
            json.dump(text, outfile)
    except Exception as e:
        print_c(f'Something went horribly wrong when attempted to write into file "{path}" this specific text "{text}"')
        print_c(e)