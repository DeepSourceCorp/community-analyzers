from slither.detectors.abstract_detector import (
    DetectorClassification,
    classification_txt,
)

__all__ = [
    "DEEPSOURCE_SEVERITY_WEIGHT_MAP",
    "SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_SEVERITY_MAP",
    "SLITHER_DETECTOR_CLASSIFICATION_DEEPSOURCE_CATEGORY_MAP",
]

DEEPSOURCE_SEVERITY_WEIGHT_MAP = {
    "minor": 50,
    "major": 60,
    "critical": 70,
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
