import inspect
from typing import Dict, List, Type, TypedDict

from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from slither.utils.command_line import output_detectors_json

__all__ = ["get_all_detector_classes", "get_all_detector_json"]


class DetectorJson(TypedDict):
    """
    Represents a Slither detector.
    ref: https://github.com/crytic/slither/blob/master/slither/utils/command_line.py#L368
    """

    rule_id: str  # custom param
    index: int
    check: str
    title: str
    impact: str
    confidence: str
    wiki_url: str
    description: str
    exploit_scenario: str
    recommendation: str


def _gen_rule_id(detector_class: Type[AbstractDetector]) -> str:
    """
    Generate unique rule ID for a Slither detector.
    ref: https://github.com/crytic/slither/blob/master/slither/utils/output.py#L91-L97
    """
    impact = detector_class.IMPACT.value
    confidence = detector_class.CONFIDENCE.value
    check_name = detector_class.ARGUMENT
    return f"{impact}-{confidence}-{check_name}"


def get_all_detector_classes() -> List[Type[AbstractDetector]]:
    """
    Returns list of classes for all of Slither's detectors.
    ref: https://github.com/crytic/slither/blob/master/tests/utils.py#L7
    """
    detectors = [getattr(all_detectors, name) for name in dir(all_detectors)]
    return [
        d for d in detectors if inspect.isclass(d) and issubclass(d, AbstractDetector)
    ]


def get_all_detector_json() -> List[Dict[str, DetectorJson]]:
    """
    Returns list of `DetectorJson` dicts for all of Slither's detectors.
    ref: https://github.com/crytic/slither/blob/master/slither/utils/command_line.py#L321
    """
    detectors_classes = get_all_detector_classes()
    detectors_jsons = output_detectors_json(detectors_classes)
    detector_class2json_map = {
        next(
            (d for d in detectors_classes if d.ARGUMENT == detector_json["check"])
        ): detector_json
        for detector_json in detectors_jsons
    }
    return [
        {
            **detector_json,
            "rule_id": _gen_rule_id(detector_class),
        }
        for detector_class, detector_json in detector_class2json_map.items()
    ]
