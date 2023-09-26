import json
import os
from dataclasses import dataclass

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
with open(f"{DATA_DIR}/language_extensions.json", "r") as f:
    language_extensions = json.load(f)


@dataclass
class Problem:
    title: str = ""
    url: str = ""
    solution_code: str = ""
    solution_language: str = ""

    @property
    def solution_filename(self):
        _id, *words = self.title.split()
        return f"{_id}{'-'.join(words)}{language_extensions[self.solution_language]}"

    @property
    def _id(self):
        return self.title.split(".")[0]
