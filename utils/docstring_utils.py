import os

import __init__


def get_docstring_from_readlines(lines):
    docstring_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('"""'):
            # We've found the start of the docstring
            docstring_lines.append(line.strip())
            break

    for line in lines[i + 1:]:
        if line.strip().endswith('"""'):
            # We've found the end of the docstring
            docstring_lines.append(line.strip())
            break
        else:
            docstring_lines.append(line.strip())

    docstring = '\n'.join(docstring_lines[1:-1])
    return docstring.strip() if docstring else None


def get_docstring_from_file(filename):
    filename = os.path.normpath(filename)
    with open(filename) as f:
        lines = f.readlines()
    return get_docstring_from_readlines(lines)





import re

def get_metadata_from_docstring(docstring):
    metadata_regex = r'^\s*([A-Za-z0-9_-]+)\s*:\s*(.*)$'
    metadata = {}
    current_key = None
    current_value_lines = []

    for line in docstring.split('\n'):
        match = re.match(metadata_regex, line)
        if match:
            if current_key is not None:
                current_value = '\n'.join(current_value_lines)
                metadata[current_key] = current_value

            current_key, current_value_lines = match.groups()
            current_value_lines = [current_value_lines.strip()]
        elif current_key is not None and line.strip().startswith(' '):
            current_value_lines.append(line.strip())
        else:
            if current_key is not None:
                current_value = '\n'.join(current_value_lines)
                metadata[current_key] = current_value

            current_key = None
            current_value_lines = []

    if current_key is not None:
        current_value = '\n'.join(current_value_lines)
        metadata[current_key] = current_value

    return metadata






docstring =get_docstring_from_file("C:/Users/mpaka/PycharmProjects/fuse_framework/endpoints/py_runnable_endpoint_template.py")
metadata = get_metadata_from_docstring(docstring)
print()