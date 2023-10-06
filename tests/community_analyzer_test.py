import json
import os
from pathlib import Path

import run_community_analyzer


def test_community_analyzer(tmp_path: Path) -> None:
    toolbox_path = tmp_path.as_posix()
    # TODO: Add a kubelinter output in the test folder
    artifacts_path = os.path.join(os.path.dirname(__file__), "test_artifacts")

    os.environ["TOOLBOX_PATH"] = toolbox_path
    os.environ["ARTIFACTS_PATH"] = artifacts_path
    run_community_analyzer.main(["--analyzer=kube-linter"])

    analysis_results = tmp_path / "analysis_results.json"
    assert analysis_results.exists()

    with open(analysis_results) as file:
        result = json.load(file)

    assert result == {
        "issues": [],  # TODO
        "errors": [],
        "metrics": [],
        "is_passed": True,
        "extra_data": {},
    }
