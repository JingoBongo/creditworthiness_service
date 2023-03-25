import sys

from utils import constants as c
import shutil

# define the path to the input text file
input_file = f"{c.resources_folder_full_path}/code_or_text_templates/fuse.service"

# read the contents of the input file
with open(input_file, "r") as f:
    text = f.read()

# replace the placeholder string with the desired value
placeholder = "<path_to_fuse>"
replacement2 = f"{c.root_path[:-1]}"
replacement = f"{replacement2}fuse.py"
placeholder2 = '<path_to_fuse_root>'
modified_text = text.replace(placeholder, replacement)
modified_text = text.replace(placeholder2, replacement2)

# define the path to the output text file
if len(sys.argv) > 1:
    with open(f"{sys.argv[1]}/fuse.service", 'w') as f:
        f.write(modified_text)
else:
    with open("/etc/systemd/system/fuse.service", 'w') as f:
        f.write(modified_text)
