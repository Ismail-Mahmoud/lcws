import json
import os
from dataclasses import dataclass

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
with open(f"{DATA_DIR}/languages.json", "r") as f:
    languages = json.load(f)


@dataclass
class Problem:
    title: str = ""
    url: str = ""
    solution_code: str = ""
    solution_language: str = ""

    @property
    def solution_filename(self):
        _id, *words = self.title.split()
        file_ext = languages.get(self.solution_language, {})\
                            .get("file_extension", "")
        return f"{_id}{'-'.join(words)}{file_ext}"

    @property
    def solution_file_content(self):
        comment_symbol = languages.get(self.solution_language, {})\
                                  .get("comment_symbol", "")
        file_content = f"{comment_symbol} {self.url}\n\n" if comment_symbol else ""
        file_content += f"{self.solution_code}\n"
        return file_content

    @property
    def _id(self):
        return self.title.split(".")[0]
