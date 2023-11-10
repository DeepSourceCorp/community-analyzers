import os
import tempfile
from typing import List

from constants import ISSUE_MD_TEMPLATE
from extractor import Issue, IssueExtractor
from issue_map_gen import generate_mapping


def get_issue_content(title, description, category, verbose_name) -> str:
    """Return the content of the toml file."""
    return ISSUE_MD_TEMPLATE.format(
        title=title,
        description=description,
        category=category,
        verbose_name=verbose_name,
    )


def get_issue_filepath(issue_code: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        f".deepsource/issues/{issue_code}.md",
    )


def update_issues(issues: List[Issue]) -> None:
    """Create/Update issue toml files."""
    # Generate new mapping
    mapping = generate_mapping(issues=issues)

    for issue in issues:
        issue_code = mapping[issue.code]["issue_code"]
        filepath = get_issue_filepath(issue_code)
        content = get_issue_content(
            issue.title, issue.description, issue.category, issue.code
        )

        with open(filepath, "w") as f:
            f.write(content)


if __name__ == "__main__":
    issues = []
    with tempfile.TemporaryDirectory() as d:
        extractor = IssueExtractor(d)
        issues = extractor.issues

    update_issues(issues=issues)
