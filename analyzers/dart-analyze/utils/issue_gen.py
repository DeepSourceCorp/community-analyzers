import os
from typing import List

from constants import ISSUE_TOML_TEMPLATE
from extractor import Issue, IssueExtractor
from issue_map_gen import generate_mapping


def get_issue_content(
    title: str, description: str, category: str, verbose_name: str
) -> str:
    """Return the content of the toml file."""
    return ISSUE_TOML_TEMPLATE.format(
        title=title,
        description=description,
        category=category,
        verbose_name=verbose_name,
    )


def get_issue_filepath(issue_code: str) -> str:
    """Returns the file path of the given issue code."""
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        f".deepsource/issues/{issue_code}.toml",
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


def main() -> None:
    """Entrypoint for this script."""
    extractor = IssueExtractor()
    issues = extractor.issues
    update_issues(issues=issues)


if __name__ == "__main__":
    main()
