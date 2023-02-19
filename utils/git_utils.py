import __init__

import os
from github import GithubException
from github.MainClass import Github
from utils import logger_utils as log
import yaml
from utils import encryption_utils as enc
from utils.decorators.exceptions_catcher_decorator import catch_exceptions


@catch_exceptions(GithubException)
def get_repository_file_list(repository):
    g = Github()
    repo = g.get_repo(repository)
    files = [f.path for f in repo.get_contents("")]
    return files


@catch_exceptions(GithubException)
def get_generic_file_from_repository(repository, full_file_path):
    g = Github()
    repo = g.get_repo(repository)
    return repo.get_contents(full_file_path).decoded_content.decode()


@catch_exceptions(GithubException)
def get_yaml_file_from_repository(repository, full_file_path):
    g = Github()
    repo = g.get_repo(repository)
    return yaml.safe_load(repo.get_contents(full_file_path).decoded_content.decode())


@catch_exceptions(GithubException)
def modify_yaml_file(repository, full_file_path, new_file_contents):
    access_token = enc.get_secured_token()
    g = Github(login_or_token=access_token)
    repo = g.get_repo(repository)
    file_contents = repo.get_contents(full_file_path)
    new_yaml_contents = yaml.safe_dump(new_file_contents, default_flow_style=False)
    repo.update_file(full_file_path, f"Updated yaml file {full_file_path}", new_yaml_contents, file_contents.sha)


@catch_exceptions(GithubException)
def modify_generic_file(repository, full_file_path, new_file_contents):
    access_token = enc.get_secured_token()
    g = Github(login_or_token=access_token)
    repo = g.get_repo(repository)
    repo.update_file(full_file_path, f"Updated file {full_file_path}", new_file_contents,
                     repo.get_contents(full_file_path).sha)


@catch_exceptions(GithubException)
def delete_generic_file(repository, full_file_path):
    access_token = enc.get_secured_token()
    g = Github(access_token)
    repo = g.get_repo(repository)
    file_contents = repo.get_contents(full_file_path)
    repo.delete_file(full_file_path, f"Deleted file {full_file_path}", file_contents.sha)


@catch_exceptions(GithubException)
def download_file_and_save(repository, repo_file_path_plus_file_name, local_save_path_plus_file_name):
    g = Github()
    repo = g.get_repo(repository)
    file_content = repo.get_contents(repo_file_path_plus_file_name).decoded_content
    with open(local_save_path_plus_file_name, 'wb') as f:
        f.write(file_content)
    log.info(f"File downloaded and saved to {local_save_path_plus_file_name}")


@catch_exceptions(GithubException)
def upload_file_to_github(repository, file_path):
    access_token = enc.get_secured_token()
    g = Github(access_token)
    repo = g.get_repo(repository)
    base_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_content = f.read()
        # I am not sure about 'Expected type 'str', got 'bytes' instead ' with file_content below, but be aware
        repo.create_file(base_name, f"Uploaded file {base_name} to {repository}", file_content)
        log.info(f"File '{base_name}' uploaded to {repository}")

# repo_name = "JingoBongo/fuse_cloud_repo"
# yaml_file = 'youtube_used_vids_list.yaml'
# readme_file = 'README.md'
