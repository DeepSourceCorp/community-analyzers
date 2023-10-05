"""
This script is responsible to scrape issues from infer's documentation, and create separate md files
for DeepSource to register them.

Infer doesn't provide issue codes for the issues it detects, so we'd be using a mapping to take care
of it. DeepSource expects an issue code for all issues.

Note: The script heavily depends on the directory structure, and would break if the structure is
changed. The maintainers should pay attention to making sure this is updated all the time.
"""
import pathlib
import os
import subprocess
from tempfile import TemporaryDirectory


ISSUES_FOLDER = os.path.join(os.path.abspath(__file__), "issues")
ISSUE_MAP = ""
CLONE_URL = "https://github.com/facebook/infer.git"


def clone_issues_locally():
    """Clone the issues directory from infer's GitHub repo."""
    clone_command = f"git clone {CLONE_URL} --depth=1".split()
    with TemporaryDirectory() as temp_dir_name:
        subprocess.run(clone_command, cwd=temp_dir_name)
        infer_issues_dir = f"{temp_dir_name}/infer/infer/documentation/issues"
        for filename in os.listdir(infer_issues_dir):
            if not filename.endswith(".md"):
                pass
            infer_issue_id = filename.removesuffix(".md")

clone_issues_locally()
