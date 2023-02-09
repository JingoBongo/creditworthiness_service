import json

from github.MainClass import Github
from github.Repository import Repository

import __init__


from utils import yaml_utils
from utils import constants as c
from utils import logger_utils as log
from utils import encryption_utils as enc
from github import Github as g

import requests
import yaml

# username = yaml_utils.get_cloud_repo_username_from_config()
# password = enc.decrypt_string(enc.load_key(), enc.load_encrypted_string(c.secret_path))
# repo_url = yaml_utils.get_cloud_repo_from_config()


def read_data_from_yaml(file_path):
    username = yaml_utils.get_cloud_repo_username_from_config()
    password = enc.decrypt_string(enc.load_key(), enc.load_encrypted_string(c.secret_path))
    repository = yaml_utils.get_cloud_repo_from_config()
    file_url = f"https://raw.githubusercontent.com/{repository}/master/{file_path}"
    response = requests.get(file_url, auth=(username, password))
    if response.status_code == 200:
        data = yaml.safe_load(response.text)
        return data
    else:
        raise Exception(f"Failed to read file from repository. Response code: {response.status_code}")

def modify_yaml_in_github(file_path, data):
    username = yaml_utils.get_cloud_repo_username_from_config()
    password = enc.decrypt_string(enc.load_key(), enc.load_encrypted_string(c.secret_path))
    access_token = "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"
    repository = yaml_utils.get_cloud_repo_from_config()
    commit_message = "list modification"
    encoded_content = yaml.safe_dump(data).encode('utf-8')
    file_url = f"https://api.github.com/repos/{repository}/contents/{file_path}"
    headers = {
        "Authorization": f"Token {access_token}",
        "Content-Type": "application/json"
    }
    get_response = requests.get(file_url, auth=(username, access_token))
    sha = get_response.json()["sha"]
    payload = {
        "message": commit_message,
        "content": encoded_content.decode('utf-8'),
        "sha": sha
    }
    response = requests.put(file_url, auth=(username, access_token), headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to modify file. Response code: {response.status_code}")

def this_at_least_works(repository, file):
    ppassword = enc.decrypt_string(enc.load_key(), enc.load_encrypted_string(c.secret_path))
    github = Github(login_or_token = "FuseFrameworkRobot", password=ppassword)
    # repo = Repository(full_name_or_id="JingoBongo/fuse_framework")
    repo = github.get_repo(full_name_or_id = "JingoBongo/fuse_cloud_repo")
    print(repo.name)

# print(this_at_least_works("FuseFrameworkRobot/fuse_cloud_repo", "youtube_used_vids_list.yaml"))

data = read_data_from_yaml("youtube_used_vids_list.yaml")
print(data)
data['list'].append('kekekw')
modify_yaml_in_github("youtube_used_vids_list.yaml", data)
data = read_data_from_yaml("youtube_used_vids_list.yaml")
print(data)