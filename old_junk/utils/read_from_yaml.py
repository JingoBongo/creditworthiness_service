import yaml
from old_junk.utils import general_utils as g


def read_from_yaml(file_path):
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except:
        g.printc(f"error reading {file_path} file")
        return [f"error reading {file_path} file", ]
