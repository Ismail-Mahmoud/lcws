import os
import re
import tomllib
from urllib.parse import urljoin

import requests
from click import ClickException

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
with open(f"{CONFIG_DIR}/config.toml", "rb") as f:
    config = tomllib.load(f)


def match_url(pattern: str, url: str):
    """Match a url to a given pattern"""
    result = re.match(pattern, url)
    if result is None:
        return result
    return result.group()


def validate_url(url: str | None):
    try:
        res = requests.get(url)  # type: ignore
        res.raise_for_status()
    except:
        raise ClickException("Invalid problem url.")


def parse_url(url: str):
    """Return problem and submission urls"""
    BASE_URL = config["leetcode"]["base_url"]
    PROBLEM_URL_PATTERN = urljoin(BASE_URL, "problems/[\w|-]+/")
    SUBMISSION_URL_PATTERN = urljoin(PROBLEM_URL_PATTERN, "submissions/\d+/")

    problem_url = match_url(PROBLEM_URL_PATTERN, url)
    submission_url = match_url(SUBMISSION_URL_PATTERN, url)

    return problem_url, submission_url
