import os
from textwrap import dedent

from issue_map_gen import generate_mapping, get_issue_map, get_issues_json


def get_toml_content(title, description, remediation) -> str:
    """Return the content of the toml file."""
    content = f'''
    title = "{title}"
    severity = "major"
    category = "antipattern"
    weight = 70
    description = """
    {description}

    <!--more-->

    ## Remediation
    {remediation}
    """
    '''
    return dedent(content)


def update_issue_tomls() -> None:
    """Create issue toml files."""
    # Generate new mapping
    generate_mapping()
    mapping = get_issue_map()

    # Get the list of issues from kubelinter
    kubelinter_cli_issues = get_issues_json()
    for issue in kubelinter_cli_issues:
        issue_name = issue["name"]
        issue_code = mapping[issue_name]["issue_code"]

        filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            f".deepsource/issues/{issue_code}.toml",
        )
        if os.path.exists(filepath):
            continue

        description = issue["description"]
        remediation = issue["remediation"]
        content = get_toml_content(issue_name, description, remediation)
        with open(filepath, "w") as f:
            f.write(content)


if __name__ == "__main__":
    update_issue_tomls()
