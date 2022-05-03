import yaml


# from utils import general_utils as g


def read_from_yaml(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print('*not a proper print*')
        print(str(e))
        print(f"*not a proper print* error reading {file_path} file")
        # raise Exception(e)
        # return [f"error reading {file_path} file", ]
