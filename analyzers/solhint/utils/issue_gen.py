import os
from textwrap import dedent

from constants import ISSUES_DIR
from issue_map_gen import generate_mapping, get_issue_map
from rules import get_all_rules


def _get_toml_path(issue_code: str) -> str:
    """Returns the file path to a issue toml for given `issue_code`."""
    return os.path.join(ISSUES_DIR, f"{issue_code}.toml")


def get_toml_content(
    title: str,
    verbose_name: str,
    severity: str,
    category: str,
    weight: int,
    description: str,
    bad_practice: str,
    good_practice: str,
    learn_more: str,
) -> str:
    """Return the content of the toml file."""
    bad_practice_section = (
        f"\n\n## Not Recommended(s)\n{bad_practice}" if bad_practice else ""
    )
    good_practice_section = (
        f"\n\n## Recommended\n{good_practice}" if good_practice else ""
    )
    learn_more_section = f"\n\n## Learn more\n{learn_more} on Solhint's documentation."

    content = f'''title = "{title}"
verbose_name = "{verbose_name}"
severity = "{severity}"
category = "{category}"
weight = {weight}
description = """
{description}

<!--more-->{bad_practice_section}{good_practice_section}{learn_more_section}
"""
    '''

    return dedent(content)


def update_issue_tomls() -> None:
    """Create issue toml files."""
    # Generates mapping if doesn't exist and then read it
    generate_mapping()
    mapping = get_issue_map()

    rules = get_all_rules()

    # For each Solhint rule,
    # create a DeepSource equivalent .toml issue file
    for rule in rules:
        rule_id = rule.rule_id
        issue_code = mapping[rule_id]["issue_code"]

        filepath = _get_toml_path(issue_code)

        title = rule.description.removesuffix(".").replace('"', "`")
        wiki_url = rule.wiki_url
        description = rule.description
        bad_practice = "\n\n".join(
            (
                f"{idx}. {bad_example['description']}\n"
                + "```solidity\n"
                + bad_example["code"]
                + "\n```"
            )
            for idx, bad_example in enumerate(rule.bad_examples, start=1)
        )
        good_practice = "\n\n".join(
            (
                f"{idx}. {good_example['description']}\n"
                + "```solidity\n"
                + good_example["code"]
                + "\n```"
            )
            for idx, good_example in enumerate(rule.good_examples, start=1)
        )
        severity = rule.deepsource_severity
        category = rule.deepsource_category
        weight = rule.deepsource_weight

        content = get_toml_content(
            title=title,
            verbose_name=rule_id,
            severity=severity,
            category=category,
            weight=weight,
            description=description,
            bad_practice=bad_practice,
            good_practice=good_practice,
            learn_more=f"[{rule_id}]({wiki_url})",
        )
        with open(filepath, "w") as f:
            f.write(content)

    print(f"[+] Created/Updated {len(rules)} Solhint issue tomls in {ISSUES_DIR}.")


if __name__ == "__main__":
    update_issue_tomls()
