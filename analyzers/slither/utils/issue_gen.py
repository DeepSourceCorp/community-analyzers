import os
from textwrap import dedent

from constants import (
    DEEPSOURCE_SEVERITY_WEIGHT_MAP,
    SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_CATEGORY_MAP,
    SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_SEVERITY_MAP,
)
from detectors import get_all_detector_json
from issue_map_gen import generate_mapping, get_issue_map


def _get_toml_path(issue_code: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        f".deepsource/issues/{issue_code}.toml",
    )


def get_toml_content(
    title: str,
    severity: str,
    category: str,
    weight: int,
    description: str,
    exploit_scenario: str,
    recommendation: str,
    learn_more: str,
) -> str:
    """Return the content of the toml file."""
    content = f'''title = "{title}"
severity = "{severity}"
category = "{category}"
weight = {weight}
description = """
{description}

<!--more-->

## Exploit Scenario
{exploit_scenario}

## Recommendation
{recommendation}

## Learn more
{learn_more} on Slither's wiki.
"""
    '''
    return dedent(content)


def update_issue_tomls() -> None:
    """
    Create issue toml files.
    """
    # Generates mapping if doesn't exist
    generate_mapping()
    mapping = get_issue_map()

    detectors = get_all_detector_json()

    # For each Slither detector,
    # create a DeepSource equivalent .toml issue file
    for detector in detectors:
        issue_name = detector["check"]
        issue_code = mapping[issue_name]["issue_code"]

        filepath = _get_toml_path(issue_code)

        title = detector["title"]
        impact = detector["impact"]
        wiki_url = detector["wiki_url"]
        description = detector["description"]
        exploit_scenario = detector["exploit_scenario"]
        recommendation = detector["recommendation"]
        severity = SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_SEVERITY_MAP[impact]
        category = SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_CATEGORY_MAP[impact]
        weight = DEEPSOURCE_SEVERITY_WEIGHT_MAP[severity]

        content = get_toml_content(
            title=title,
            severity=severity,
            category=category,
            weight=weight,
            description=description,
            exploit_scenario=exploit_scenario,
            recommendation=recommendation,
            learn_more=f"[{issue_name}]({wiki_url})",
        )
        with open(filepath, "w") as f:
            f.write(content)


if __name__ == "__main__":
    update_issue_tomls()
