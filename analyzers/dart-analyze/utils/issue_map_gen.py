import itertools
import json
import tempfile
from typing import Dict, List

from constants import ISSUE_MAP_FILE, ISSUE_PREFIX
from extractor import Issue, IssueExtractor


def get_code_generator(mapping) -> itertools.count:
    """Return the next available issue code."""
    num_issues = len(mapping.keys())  # get the number of issues already in the mapping
    next_code = 1001 + num_issues  # issue code series starts from `1001`
    yield from itertools.count(next_code)


def get_issue_map() -> Dict[str, Dict[str, str]]:
    """Return the issue map."""
    with open(ISSUE_MAP_FILE, "r") as f:
        return json.load(f)


def generate_mapping(issues: List[Issue]) -> Dict[str, Dict[str, str]]:
    """
    Generates and returns a dict mapping of DeepSource assigned
    issue codes to Slither's detector names.

    Example mapping:
    {
        "always_declare_return_types": {"issue_code": "DART-A0001"},
    }
    """
    issue_map = get_issue_map()
    code_generator = get_code_generator(issue_map)

    if len(issues) > len(issue_map):
        # if the no. of issues in the mapping is less than the no. of detectors,
        # then generate the mapping only for the new detectors
        for issue in issues:
            if issue.code not in issue_map.keys():
                shortcode = f"{ISSUE_PREFIX}{next(code_generator)}"
                issue_map[issue.code] = {"issue_code": shortcode}

    with open(ISSUE_MAP_FILE, "w") as f:
        json.dump(issue_map, f, indent=4)

    return issue_map


if __name__ == "__main__":
    issues = []
    with tempfile.TemporaryDirectory() as d:
        extractor = IssueExtractor(d)
        issues = extractor.issues

    generate_mapping(issues=issues)
