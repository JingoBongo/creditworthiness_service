import __init__
import os
import utils.general_utils as g

all_py_local_files = []
all_imports = []


def try_import_and_install_package(package_name):
    try:
        if package_name:
            str = f"import {package_name}"
            if str:
                if len(str) > 0:
                    exec(str)
                    print(f"{package_name} is already installed")
    except ImportError:
        try:
            print(f"Trying to Install required module: {package_name}")
            os.system(f"pip install {package_name}")
        except Exception as e:
            print(f"Failed to install {package_name}, it is probably installed already")
            print(e)


def try_import_and_install_uncommon_package(import_name, module_name):
    pac_name, pac_ver = module_name.split('==')
    try:
        if import_name:
            str = f"import {import_name}"
            if str:
                if len(str) > 0:
                    exec(str)
                    print(f"{import_name} is already installed")
    except ImportError:
        try:
            try:
                version = os.popen(f"pip show {pac_name}").read()
            except:
                version = None
            if not version:
                os.system(f"pip install -Iv {module_name} --user")
                return
            for line in version.split('\n'):
                if 'Version' in line:
                    if line.split(' ')[1] == pac_ver:
                        pass
                    else:
                        #             uninstall previous version
                        os.system(f"pip uninstall {pac_name} -y")
                        #     install specified version
                        os.system(f"pip install -Iv {module_name} --user")
        except Exception as e:
            print(f"Failed to install {module_name}, check the details yourselves")
            print(e)


def check_string_has_no_occurrences_in_the_list(string, list):
    has_occurrence = True
    for l in list:
        if l in string:
            # print(f"{l} IN {string}????")
            has_occurrence = False
    return has_occurrence


def get_package_name_from_line(line):
    line = line.strip()
    # print(f"Line that got into 'get_package_name_from_file' : {line}")
    if line.startswith('import'):
        # print(f"'get_package_name_from_file' returned {line.split(' ')[1]}")
        return line.split(' ')[1]
    if 'from' in line:
        line = line.split('import')[0]
        line = line.split(' ')[1]
        line = line.split('.')[0]
        # print(f"'get_package_name_from_file' returned {line}")
        return line
    else:
        print(f"Dafuq is this line? : {line}")


def is_local_import(line):
    for py in all_py_local_files:
        if py in line:
            # print(f"{line} is local")
            return True
    # print(f"{line} is NOT local")
    return False


def find_used_packages():
    global all_py_local_files
    global all_imports
    restricted_folders = ['orchestra_env', 'test1env_withoutml', 'empty_env']
    root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')

    for root, dirs, files in os.walk(root_path):
        for file in files:
            file_full_path = os.path.join(root, file)
            if file.endswith(".py") and check_string_has_no_occurrences_in_the_list(file_full_path, restricted_folders):
                all_py_local_files.append(file.replace('.py', ''))
                with open(file_full_path) as f:
                    for line in f.readlines():
                        line = line.strip()
                        if line.startswith('import') or line.startswith('from'):
                            # print(f"Import line : '{line}' in file {file}")
                            line = line.replace('\n', '')
                            all_imports.append(line)
    all_imports = [im for im in all_imports if not is_local_import(im)]
    all_imports = [get_package_name_from_line(im) for im in all_imports]
    all_imports = list(set(all_imports))
    # print('all non local imports')
    # print(all_imports)
    return all_imports


def run_importing_process():
    print(f"Checking installed modules")
    for im in find_used_packages():
        try_import_and_install_package(im)
    config = g.config
    for module in config['uncommon_modules']:
        try_import_and_install_uncommon_package(config['uncommon_modules'][module]['import_name'],
                                                config['uncommon_modules'][module]['module_name'])
    print(f"Modules preparation complete")

# run_importing_process()
# print('local files')
# print(all_py_local_files)
