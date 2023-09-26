import json
import os
import tomllib
from pathlib import Path
from typing import TypeAlias

import requests
from click import ClickException

SHA: TypeAlias = str

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
with open(f"{CONFIG_DIR}/config.toml", "rb") as f:
    config = tomllib.load(f)

BASE_URL = config["github"]["api_base_url"].rstrip("/")
ACCESS_TOKEN = config["github"]["access_token"]
OWNER = config["github"]["owner"]
REPO = config["github"]["repo"]
BRANCH = config["github"]["branch"]
DIRECTORY = config["github"]["directory"].rstrip("/")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_head_ref() -> SHA:
    """Return the head reference of the branch (last commit SHA)."""
    url = "/".join([BASE_URL, OWNER, REPO, "git/refs/heads", BRANCH])
    res = requests.get(url)
    return res.json()["object"]["sha"]


def create_tree(content: str, filename: str, base_tree: SHA) -> SHA:
    """Create a Git tree with the solution file.

    :param content: solution file content
    :param filename: solution file name
    :param base_tree: last commit SHA

    :return: the created tree SHA
    """
    url = "/".join([BASE_URL, OWNER, REPO, "git/trees"])
    data = {
        "base_tree": base_tree,
        "tree": [{
            "path": "/".join([DIRECTORY.rstrip("/"), filename]),
            "mode": "100644",
            "type": "blob",
            "content": content,
        }]
    }
    res = requests.post(url, data=json.dumps(data), headers=HEADERS)
    return res.json()["sha"]


def create_commit(commit_message: str, tree: SHA, parent: SHA) -> tuple[SHA, str]:
    """Create a new commit referencing the newly-created tree.

    :param commit_message: commit message
    :param tree: the tree SHA which will be referenced by this commit
    :param parent: last commit SHA

    :return: the SHA and URL of the new commit
    """
    url = "/".join([BASE_URL, OWNER, REPO, "git/commits"])
    data = {
        "message": commit_message,
        "tree": tree,
        "parents": [parent],
    }
    res = requests.post(url, data=json.dumps(data), headers=HEADERS)
    return res.json()["sha"], res.json()["html_url"]


def update_head_ref(new_ref: SHA) -> None:
    """Update the head reference of the branch to point to the new commit.

    :param new_ref: the new commit SHA
    """
    url = "/".join([BASE_URL, OWNER, REPO, "git/refs/heads", BRANCH])
    data = {
        "sha": new_ref
    }
    requests.patch(url, data=json.dumps(data), headers=HEADERS)


def upload_to_github(solution: str, filename: str, commit_message: str) -> str:
    """Upload a solution to GitHub using GitHub API.

    :param solution: solution code
    :param filename: name of the file to be created
    :param commit_message: commit message

    :return: URL of the new commit
    """
    solution += "\n"

    try:
        head_ref = get_head_ref()
    except:
        raise ClickException(
            "Couldn't fetch the head reference of the specified branch.")

    try:
        tree = create_tree(
            content=solution, filename=filename, base_tree=head_ref)
    except:
        raise ClickException("Error while creating the Git tree.")

    try:
        commit_sha, commit_url = create_commit(
            commit_message=commit_message, tree=tree, parent=head_ref)
    except:
        raise ClickException("Error while creating the new commit.")

    try:
        update_head_ref(new_ref=commit_sha)
    except:
        raise ClickException("Couldn't update the head reference.")

    return commit_url
