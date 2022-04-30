import json
import os


def printc(msg):
    print(msg)

def run_cmd_command(command):
    printc(f'triggering command :{command}')
    returned_value = os.system(command)
    printc(f'returned value: {returned_value}')


def read_from_json(path):
    try:
        with open(path) as json_file:
            return json.load(json_file)
    except:
        printc(f'Something went horribly wrong when attempted to read from file "{path}"')
        return {}


def write_to_json(path, text):
    try:
        with open(path, 'w') as outfile:
            json.dump(text, outfile)
    except:
        printc(f'Something went horribly wrong when attempted to write into file "{path}" this specific text "{text}"')


def clear_busy_ports(path):
    new_json = {"busy_ports": ['5000']}
    write_to_json(path, new_json)