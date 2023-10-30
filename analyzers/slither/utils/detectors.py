import inspect
from typing import Dict, List, Type, Union

from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from slither.utils.command_line import output_detectors_json

__all__ = ["get_all_detector_classes", "get_all_detector_json"]


def get_all_detector_classes() -> List[Type[AbstractDetector]]:
    # ref: https://github.com/crytic/slither/blob/master/tests/utils.py#L7
    detectors = [getattr(all_detectors, name) for name in dir(all_detectors)]
    return [
        d for d in detectors if inspect.isclass(d) and issubclass(d, AbstractDetector)
    ]


def get_all_detector_json() -> List[Dict[str, Dict[str, Union[str, int]]]]:
    # ref: https://gitbub.com/crytic/slither/blob/master/slither/utils/command_line.py#L321
    detector_classes = get_all_detector_classes()
    return output_detectors_json(detector_classes)
