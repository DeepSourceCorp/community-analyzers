import os
import tempfile
from typing import List

from extractor import Issue, IssueExtractor
from issue_map_gen import generate_mapping


def get_toml_content(title, description, category, verbose_name) -> str:
    """Return the content of the toml file."""
    return f'''
title = "{title}"
verbose_name = "{verbose_name}"
severity = "major"
category = "{category}"
weight = 70
description = """
{description}
"""
'''


def get_issue_toml_filepath(issue_code: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        f".deepsource/issues/{issue_code}.toml",
    )


def update_issue_tomls(issues: List[Issue]) -> None:
    """Create/Update issue toml files."""
    # Generate new mapping
    mapping = generate_mapping(issues=issues)

    for issue in issues:
        issue_code = mapping[issue.code]["issue_code"]
        filepath = get_issue_toml_filepath(issue_code)
        contents = get_toml_content(
            issue.title, issue.description, issue.category, issue.code
        )

        with open(filepath, "w") as f:
            f.write(contents)


if __name__ == "__main__":
    issues = []
    with tempfile.TemporaryDirectory() as d:
        extractor = IssueExtractor(d)
        issues = extractor.issues

    update_issue_tomls(issues=issues)
