import yaml
import os


cur_file_name = os.path.basename(__file__)

def print_c(text):
    print(f"[{cur_file_name}] {str(text)}")


def read_from_yaml(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print_c('*not a proper print*')
        print_c(e)
        print_c(f"*not a proper print* error reading {file_path} file")
        # raise Exception(e)
        # return [f"error reading {file_path} file", ]
