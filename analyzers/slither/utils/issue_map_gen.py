import json

from constants import ISSUE_MAP_FILE, ISSUE_PREFIX, ZEROES_PADDING_LENGTH
from detectors import DetectorJson, get_all_detector_json
from slither.detectors.abstract_detector import DetectorClassification

__all__ = ["get_issue_map", "generate_mapping"]


def _gen_issue_id(detector: DetectorJson) -> str:
    # ref: https://github.com/crytic/slither/blob/master/slither/utils/output.py#L91
    impact = DetectorClassification[detector["impact"].upper()].value
    confidence = DetectorClassification[detector["confidence"].upper()].value
    return f"{impact}-{confidence}-{detector['check']}"


def _gen_issue_code(detector: DetectorJson) -> str:
    return f"{ISSUE_PREFIX}{detector['index']:0{ZEROES_PADDING_LENGTH}d}"


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

    return {
        _gen_issue_id(detector): {"issue_code": _gen_issue_code(detector)}
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
