import itertools
import json
from typing import Dict, Iterator

from constants import ISSUE_MAP_FILE, ISSUE_PREFIX
from detectors import get_all_detector_json

__all__ = ["get_issue_map", "generate_mapping"]


def _get_next_code(mapping: Dict[str, Dict[str, str]]) -> Iterator[int]:
    """Return the next available issue code."""
    num_issues = len(mapping.keys())  # get the number of issues already in the mapping
    next_code = 1001 + num_issues  # issue code series starts from `1001`
    yield from itertools.count(next_code)


def get_issue_map() -> Dict[str, Dict[str, str]]:
    """Return the issue map."""
    with open(ISSUE_MAP_FILE, "r") as f:
        return json.load(f)


def get_mapping() -> Dict[str, Dict[str, str]]:
    """Generates and returns a dict mapping of DeepSource assigned issue codes to Slither's detector names."""
    # Example mapping:
    # {
    #     "0-0-abiencoderv2-array": {"issue_code": "SLITHER-W0001"},
    # }
    issue_map = get_issue_map()
    generate_code = _get_next_code(issue_map)
    detectors = get_all_detector_json()

    if len(detectors) > len(issue_map):
        # if the no. of issues in the mapping is less than the no. of detectors,
        # then generate the mapping only for the new detectors
        for detector in detectors:
            if detector["rule_id"] not in issue_map:
                next_code = next(generate_code)
                issue_map[detector["rule_id"]] = {
                    "issue_code": f"{ISSUE_PREFIX}{next_code}"
                }

    return issue_map


def generate_mapping() -> None:
    """Generates and dumps a dict mapping of DeepSource assigned issue codes to Slither's detector names in `issue_map.json` file."""
    issue_map = get_mapping()
    # dump mapping into file
    with open(ISSUE_MAP_FILE, "w") as f:
        json.dump(issue_map, f, indent=4)


if __name__ == "__main__":
    generate_mapping()
