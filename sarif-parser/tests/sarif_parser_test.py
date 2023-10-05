import json
import os.path

import pytest

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
    with open(deepsource_file_path) as file:
        expected_output = json.load(file)

    with open(sarif_file_path) as sarif_file:
        sarif_data = json.load(sarif_file)

    assert sarif_parser.parse(sarif_data) == expected_output
