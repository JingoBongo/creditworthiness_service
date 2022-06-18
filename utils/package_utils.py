import __init__
import subprocess
import tempfile
from utils import constants as c



import os

all_py_local_files = []
all_imports = []
# root_path = os.path.dirname(os.path.abspath(__file__)).replace('utils', '')
root_path = c.root_path
# conf_path = os.path.normpath('.//resources//fuse.yaml')
conf_path = c.conf_path



def progress_bar(progress, total, text=''):
    percent = 100* (progress / float(total))
    bar = '■' * int(percent) + '-'*(100-int(percent))
    print(f"\r|{bar}| {percent:.2f}% : {str(text)}", end = "\r")


def try_import_and_install_package(package_name):
    try:
        if package_name:
            str = f"import {package_name}"
            if str:
                if len(str) > 0:
                    exec(str)
                    # print(f"{package_name} is already installed")
    except ImportError:
        try:
            print(f"Trying to Install required module: {package_name} --user")
            os.system(f"pip3 install {package_name}")
        except Exception as e:
            print(f"Failed to install {package_name}, it is probably installed already")
            print(e)


def try_import_and_install_uncommon_package(import_name, pac_name, pac_ver):
    # pac_name
    if not pac_ver == 'any':
        module_postfix = '=='+pac_ver
    else:
        module_postfix = ''
    try:
        try:
            # tries to find module locally
            cmd = ['pip3', 'show', pac_name]
            with tempfile.TemporaryFile() as tempf:
                proc = subprocess.Popen(cmd, stdout=tempf)
                proc.wait()
                tempf.seek(0)
                version = tempf.read()
        except:
            version = None
        version = str(version)
        # if module isn't installed locally, install it
        if not version or len(version) < 20:
            os.system(f"pip3 install -Iv {pac_name}{module_postfix}")
            return
        # if there is actually some version of it, find the version
        for line in version.split('\\r\\n'):
            if 'Version' in line:
                # if version corresponds to config version
                if line.split(' ')[1] == pac_ver or pac_ver == 'any':
                    pass
                else:
                    #     uninstall previous version
                    os.system(f"pip3 uninstall {pac_name} -y")
                    #     install specified version
                    os.system(f"pip3 install -Iv {pac_name}{module_postfix}")

    except Exception as e:
        # print(f"Failed to install {pac_name}, check the details yourselves")
        # print(e)
        print(f"Failed to install {pac_name}, check the details yourselves")
        print(e)


def check_string_has_no_occurrences_in_the_list(string, list):
    has_occurrence = True
    for l in list:
        if l in string:
            # print(f"{l} IN {string}????")
            has_occurrence = False
    return has_occurrence


def get_package_name_from_line(line):
    try:
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
            return 'os'
    except:
        return 'os'


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
    root_path = c.root_path

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


def read_from_yaml(file_path):
    try:
        import yaml
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        # print(e)
        # print(f"*not a proper print* error reading {file_path} file")
        print(e)
        print(f"*not a proper print* error reading {file_path} file")

def run_importing_process():
    print(f"Checking installed modules")
    ind = 1
    used_packages = find_used_packages()
    progress_bar(ind, len(used_packages))
    for im in used_packages:
        progress_bar(ind, len(used_packages), f"processing : {im}")
        try_import_and_install_package(im)
        ind += 1
    print()
    print(f"Checking installed uncommon modules from config")
    try:
        # os.system(f"pip3 install -Iv pyyaml")
        try_import_and_install_uncommon_package('pyyaml', 'pyyaml', 'any')
    except:
        print('PYYAML should be already installed')
    config = read_from_yaml(root_path + conf_path)
    try:
        for module in config['uncommon_modules']:
            try_import_and_install_uncommon_package(config['uncommon_modules'][module]['import_name'],
                                                    config['uncommon_modules'][module]['module_name'],
                                                    config['uncommon_modules'][module]['module_version'])
    except Exception as e:
        print(f"Modules preparation complete")

# run_importing_process()
# print('local files')
# print(all_py_local_files)
