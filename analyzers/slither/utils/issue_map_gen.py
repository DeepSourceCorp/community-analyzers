import json
from typing import Dict

from constants import ISSUE_MAP_FILE, ISSUE_PREFIX, ZEROES_PADDING_LENGTH
from detectors import DetectorJson, get_all_detector_classes, get_all_detector_json

__all__ = ["get_issue_map", "generate_mapping"]


def _gen_issue_id(detector: DetectorJson) -> str:
    # ref: https://github.com/crytic/slither/blob/master/slither/utils/output.py#L90
    detectors_classes = get_all_detector_classes()
    detector_class = next(
        (d for d in detectors_classes if d.ARGUMENT == detector["check"])
    )
    impact = detector_class.IMPACT.value
    confidence = detector_class.CONFIDENCE.value
    # ref: https://github.com/crytic/slither/blob/master/slither/utils/output.py#L91-L97
    return f"{impact}-{confidence}-{detector['check']}"


def _gen_issue_code(detector: DetectorJson) -> str:
    return f"{ISSUE_PREFIX}{detector['index']:0{ZEROES_PADDING_LENGTH}d}"


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
