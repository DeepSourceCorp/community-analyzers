import json
import os.path

import pytest
from pathlib import Path
from unittest.mock import patch, call, MagicMock


import sarif_parser


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Generates all sarif_parser tests based on files in the sarif_files folder."""
    test_files_path = os.path.join(os.path.dirname(__file__), "sarif_files")

    test_params, test_names = [], []
    for file_name in os.listdir(test_files_path):
        if not file_name.endswith(".sarif"):
            continue

        deepsource_file_name = file_name + ".json"
        deepsource_file_path = os.path.join(test_files_path, deepsource_file_name)
        if not os.path.isfile(deepsource_file_path):
            raise AssertionError(
                f"Output file {deepsource_file_name!r} for {file_name!r} doesn't exist"
            )

        sarif_file_path = os.path.join(test_files_path, file_name)
        test_params.append((sarif_file_path, deepsource_file_path))
        test_names.append(file_name)

    metafunc.parametrize(
        ("sarif_file_path", "deepsource_file_path"),
        test_params,
        ids=test_names,
    )


def test_sarif_parser(sarif_file_path: str, deepsource_file_path: str) -> None:
    """Tests parsing of various SARIF outputs into DeepSource issues."""
    # skipcq: PTC-W6004 -- nothing sensitive here
    with open(deepsource_file_path) as file:
        expected_output = json.load(file)

    with open(sarif_file_path) as sarif_file:
        sarif_data = json.load(sarif_file)

    assert sarif_parser.parse(sarif_data) == expected_output


@patch("sentry.raise_info")
# skipcq: PYL-W0613
def test_sarif_parser_no_issue_map(mocked_run: MagicMock, sarif_file_path: str, deepsource_file_path: str, tmp_path: Path) -> None:
    """Assert that sentry.raise_info is called when issue map is not found."""
    artifacts_path = tmp_path / "artifacts"
    artifacts_path.mkdir()
    # Create an artifact # skipcq: PTC-W6004 -- nothing sensitive here
    with open(sarif_file_path) as fin, open(artifacts_path / "artifact1.sarif", "w") as fout:
        json.dump({'metadata': {'work_dir': '.'}, 'data': fin.read()}, fout)

    sarif_parser.run_sarif_parser(
        artifacts_path, tmp_path / "result.json", "some/random/path")

    no_issue_map_call = call('Could not find issue map at some/random/path for analyzer.')
    # since no issue map is found, there would also be calls for unsanitised issues.
    single_unsanitised_issue_call = call('Could not find issue code for rule name-not-defined in issue map.', context={'tool': 'mypy', 'version': '0.910'})

    assert mocked_run.has_calls([no_issue_map_call, single_unsanitised_issue_call])


def test_artifact_hashing(sarif_file_path: str, deepsource_file_path: str, tmp_path: Path) -> None:
    """End to end tests for when same artifacts are present in the directory."""
    artifacts_path = tmp_path / "artifacts"
    artifacts_path.mkdir()
    # Create an artifact # skipcq: PTC-W6004 -- nothing sensitive here
    with open(sarif_file_path) as fin, open(artifacts_path / "artifact1.sarif", "w") as fout:
        json.dump({'metadata': {'work_dir': '.'}, 'data': fin.read()}, fout)

    sarif_parser.run_sarif_parser(
        artifacts_path, tmp_path / "result.json", "some/random/path")

    old_results = json.load(open(tmp_path / "result.json"))

    # Now, put one more artifact in the directory
    # This is duplicate. # skipcq: PTC-W6004
    with open(sarif_file_path) as fin, open(artifacts_path / "artifact2.sarif", "w") as fout:
        json.dump({'metadata': {'work_dir': '.'}, 'data': fin.read()}, fout)

    # Run the sarif parser again
    sarif_parser.run_sarif_parser(
        artifacts_path, tmp_path / "result.json", "some/random/path")

    # make sure that the results are same
    new_results = json.load(open(tmp_path / "result.json"))
    assert old_results == new_results
