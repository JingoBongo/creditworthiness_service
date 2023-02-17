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

def try_get_file_list(repository):
    g = Github()
    repo = g.get_repo(repository)
    files = [f.filename for f in repo.get_contents("")]
    return files

def try_modify_file(repository, file):
    username = yaml_utils.get_cloud_repo_username_from_config()
    password = enc.decrypt_string(enc.load_key(), enc.load_encrypted_string(c.secret_path))
    access_token = "oauthtoken"
    repo_name = repository
    file_path = 'youtube_used_vids_list.yaml'

    # Create a PyGithub instance using your username and password or personal access token
    # g = Github(username, password)
    g = Github(login_or_token = "oauthtoken")

    # Get the repository object
    # repo = g.get_user().get_repo(repo_name)
    repo = g.get_repo(repository)

    # Get the contents of the YAML file
    file_contents = repo.get_contents(file_path).decoded_content.decode()

    # Parse the YAML file into a Python dictionary
    file_dict = yaml.safe_load(file_contents)

    # Modify the dictionary as desired
    file_dict['new_key'] = 'new_value'

    # Convert the dictionary back to YAML
    new_file_contents = yaml.dump(file_dict)

    # Create a new commit with the modified file contents
    repo.update_file(file_path, "Updated youtube_used_vids_list.yaml", new_file_contents,
                     repo.get_contents(file_path).sha)


# data = read_data_from_yaml("youtube_used_vids_list.yaml")
try_modify_file("JingoBongo/fuse_cloud_repo", 'file')
data = try_get_file_list("JingoBongo/fuse_cloud_repo")
print(data)
# data['list'].append('kekekw')
# modify_yaml_in_github("youtube_used_vids_list.yaml", data)
# data = read_data_from_yaml("youtube_used_vids_list.yaml")
# print(data)