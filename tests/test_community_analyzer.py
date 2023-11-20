import json
import os
from pathlib import Path

import pytest

from testutils import extract_filepaths_from_deepsource_json, temp_analysis_config

import run_community_analyzer

expected_result = {
    "is_passed": False,
    "issues": [
        {
            "issue_code": "KUBELIN-W1029",
            "issue_text": 'container "kube-scheduler" does not have a read-only root file system\nobject: <no namespace>/test-release-kube-scheduler apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/kube-scheduler/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1042",
            "issue_text": 'container "kube-scheduler" is not set to runAsNonRoot\nobject: <no namespace>/test-release-kube-scheduler apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/kube-scheduler/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1015",
            "issue_text": 'environment variable TASK_IMAGE_PULL_SECRET_NAME in container "runner" found\nobject: <no namespace>/test-release-runner apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/runner/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1015",
            "issue_text": 'environment variable TASK_ARTIFACT_SECRET_NAME in container "runner" found\nobject: <no namespace>/test-release-runner apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/runner/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1029",
            "issue_text": 'container "runner" does not have a read-only root file system\nobject: <no namespace>/test-release-runner apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/runner/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1042",
            "issue_text": 'container "runner" is not set to runAsNonRoot\nobject: <no namespace>/test-release-runner apps/v1, Kind=Deployment',
            "location": {
                "path": "charts/runner/templates/deployment.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1029",
            "issue_text": 'container "runner-rqlite" does not have a read-only root file system\nobject: <no namespace>/test-release-runner-rqlite apps/v1, Kind=StatefulSet',
            "location": {
                "path": "charts/runner/templates/rqlite-statefulset.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1042",
            "issue_text": 'container "runner-rqlite" is not set to runAsNonRoot\nobject: <no namespace>/test-release-runner-rqlite apps/v1, Kind=StatefulSet',
            "location": {
                "path": "charts/runner/templates/rqlite-statefulset.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1022",
            "issue_text": 'The container "wget" is using an invalid container image, "busybox". Please use images that are not blocked by the `BlockList` criteria : [".*:(latest)$" "^[^:]*$" "(.*/[^:]+)$"]\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1029",
            "issue_text": 'container "wget" does not have a read-only root file system\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1042",
            "issue_text": 'container "wget" is not set to runAsNonRoot\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1047",
            "issue_text": 'container "wget" has cpu request 0\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1047",
            "issue_text": 'container "wget" has cpu limit 0\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1048",
            "issue_text": 'container "wget" has memory request 0\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
        {
            "issue_code": "KUBELIN-W1048",
            "issue_text": 'container "wget" has memory limit 0\nobject: <no namespace>/test-release-runner-test-connection /v1, Kind=Pod',
            "location": {
                "path": "charts/runner/templates/tests/test-connection.yaml",
                "position": {
                    "begin": {"column": 1, "line": 1},
                    "end": {"column": 1, "line": 1},
                },
            },
        },
    ],
    "errors": [],
    "metrics": [],
    "extra_data": {},
}


def test_community_analyzer(tmp_path: Path) -> None:
    """Test for `run_community_analyzer.main()`, to test `issue_map.json` parsing."""
    toolbox_path = tmp_path.as_posix()
    artifacts_path = os.path.join(os.path.dirname(__file__), "test_artifacts")
    analysis_config_path = os.path.join(toolbox_path, "analysis_config.json")
    modified_files = extract_filepaths_from_deepsource_json(expected_result)
    os.environ["TOOLBOX_PATH"] = toolbox_path
    os.environ["ARTIFACTS_PATH"] = artifacts_path

    # Case: when analysis config is not present, it should raise an error.
    with pytest.raises(ValueError) as exe:
        run_community_analyzer.main(["--analyzer=kube-linter"])
    assert str(exe.value) == f"Could not find analysis config at {analysis_config_path}."

    # Case: all files from the report are present in the analysis config.
    with temp_analysis_config(analysis_config_path, modified_files):
        run_community_analyzer.main(["--analyzer=kube-linter"])

    analysis_results = tmp_path / "analysis_results.json"
    assert analysis_results.exists()

    with open(analysis_results) as file:
        result = json.load(file)

    assert result == expected_result

    # Case: only a subset of files from the report are present in the analysis config.
    # Note: There are 7 issues in this file in our report fixture.
    # See `expected_result`.
    modified_files = ["charts/runner/templates/tests/test-connection.yaml",]
    with temp_analysis_config(analysis_config_path, modified_files):
        run_community_analyzer.main(["--analyzer=kube-linter"])

    analysis_results = tmp_path / "analysis_results.json"
    assert analysis_results.exists()

    with open(analysis_results) as file:
        result = json.load(file)

    assert len(result["issues"]) == 7

    for issue in result["issues"]:
        assert issue["location"]["path"] == "charts/runner/templates/tests/test-connection.yaml"
