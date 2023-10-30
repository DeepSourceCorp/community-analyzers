import os

from slither.detectors.abstract_detector import (
    DetectorClassification,
    classification_txt,
)

__all__ = [
    "ISSUE_MAP_FILE",
    "ISSUE_PREFIX",
    "ZEROES_PADDING_LENGTH",
    "DEEPSOURCE_SEVERITY_WEIGHT_MAP",
    "SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_SEVERITY_MAP",
    "SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_CATEGORY_MAP",
]

# path to the `issue_map.json` located in the same directory as this script
ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "SLITHER-D"
ZEROES_PADDING_LENGTH = 4


DEEPSOURCE_SEVERITY_WEIGHT_MAP = {
    "minor": 40,
    "major": 60,
    "critical": 80,
}


SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_SEVERITY_MAP = {
    classification_txt[DetectorClassification.LOW]: "minor",
    classification_txt[DetectorClassification.MEDIUM]: "major",
    classification_txt[DetectorClassification.HIGH]: "critical",
    classification_txt[DetectorClassification.INFORMATIONAL]: "minor",
    classification_txt[DetectorClassification.OPTIMIZATION]: "major",
}

SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_CATEGORY_MAP = {
    classification_txt[DetectorClassification.LOW]: "antipattern",
    classification_txt[DetectorClassification.MEDIUM]: "antipattern",
    classification_txt[DetectorClassification.HIGH]: "antipattern",
    classification_txt[DetectorClassification.INFORMATIONAL]: "antipattern",
    classification_txt[DetectorClassification.OPTIMIZATION]: "performance",
}
