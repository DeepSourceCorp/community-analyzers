import json
import os

from detectors import get_all_detector_json

# path to the `issue_map.json` located in the same directory as this script
ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "SLITHER-D"
ZEROES_PADDING_LENGTH = 4


def _gen_issue_code(detector_idx: int) -> str:
    return f"{ISSUE_PREFIX}{detector_idx:0{ZEROES_PADDING_LENGTH}d}"


def get_issue_map() -> dict:
    """Return the issue map."""
    with open(ISSUE_MAP_FILE, "r") as f:
        return json.load(f)


def get_mapping() -> dict:
    """Generates and returns a dict mapping of DeepSource assigned issue codes to Slither's detector names."""
    # {
    #     "arbitrary-send-erc20": {"issue_code": "SLITHER-W0001"},
    # }
    # get all Slither detectors
    detectors = get_all_detector_json()

    # create mapping of slither detector's issue code to DeepSource issue code
    return {
        detector["check"]: {"issue_code": _gen_issue_code(detector["index"])}
        for detector in detectors
    }


def generate_mapping() -> None:
    """Generates and dumps a dict mapping of DeepSource assigned issue codes to Slither's detector names in `issue_map.json` file."""
    issue_map = get_mapping()
    # dump mapping into file
    with open(ISSUE_MAP_FILE, "w") as f:
        json.dump(issue_map, f, indent=4)


if __name__ == "__main__":
    generate_mapping()
