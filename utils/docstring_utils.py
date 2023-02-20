import __init__
import os
import ast


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

# def get_docstrings(file_path):
#     """
#     This function takes a file path as input and returns a dictionary of docstrings
#     for each function or class defined in the file.
#     """
#     with open(file_path, 'r') as file:
#         tree = ast.parse(file.read())
#     docstrings = {}
#     for node in ast.walk(tree):
#         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
#             docstrings[node.name] = ast.get_docstring(node)
#
#     return docstrings


def get_docstring_from_file(filename):
    filename = os.path.normpath(filename)
    with open(filename) as f:
        lines = f.readlines()
    return get_docstring_from_readlines(lines)




# def get_metadata_from_docstring(docstring):
#     metadata = {}
#     if docstring:
#         lines = docstring.strip().split('\n')
#         for line in lines:
#             line = line.strip()
#             if ':' in line:
#                 key, value = line.split(':', 1)
#                 metadata[key.strip()] = value.strip()
#
#                 # If the value is continued on the next line, keep reading until the end of the value
#                 while not value.strip().endswith('"') and lines:
#                     value += '\n' + lines.pop(0).strip()
#                     metadata[key.strip()] = value.strip()
#
#     return metadata


def parse_key_value_string(input_string):
    """
    Parses a string with key-value pairs separated by newlines and returns a dictionary.
    """
    result = {}
    current_key = None
    current_value = ""

    for line in input_string.split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            if current_key:
                result[current_key] = current_value.strip()
            current_key, current_value = line.split(":", 1)
            current_value = current_value.strip()
        else:
            current_value += " " + line

    if current_key:
        result[current_key] = current_value.strip()

    return result



# docstring =get_docstring_from_file("C:/Users/mpaka/PycharmProjects/fuse_framework/endpoints/py_runnable_endpoint_template.py")
# # docstring =get_docstrings("C:/Users/mpaka/PycharmProjects/fuse_framework/endpoints/py_runnable_endpoint_template.py")
# print(docstring)
# # metadata = get_metadata_from_docstring(docstring)
# metadata = parse_key_value_string(docstring)
# print(metadata)