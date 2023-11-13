import json
from pathlib import Path

import pytest
from sarif_parser.cli import cli

sarif_json = """
{
  "runs": [
    {
      "results": [
        {
          "message": {
            "text": "Container has no configured security context"
          },
          "level": "error",
          "locations": [
            {
              "physicalLocation": {
                "region": {
                  "snippet": {}
                },
                "artifactLocation": {
                  "uri": "/workspace/git/myproject/asd.yaml"
                },
                "contextRegion": {
                  "snippet": {},
                  "startLine": 1
                }
              }
            }
          ],
          "properties": {
            "issue_confidence": "HIGH",
            "issue_severity": "HIGH"
          },
          "ruleId": "container-security-context-user-group-id"
        },
        {
          "message": {
            "text": "CPU limit is not set"
          },
          "level": "error",
          "locations": [
            {
              "physicalLocation": {
                "region": {
                  "snippet": {}
                },
                "artifactLocation": {
                  "uri": "/workspace/git/myproject/asd.yaml"
                },
                "contextRegion": {
                  "snippet": {},
                  "startLine": 1
                }
              }
            }
          ],
          "properties": {
            "issue_confidence": "HIGH",
            "issue_severity": "HIGH"
          },
          "ruleId": "container-resources"
        }
      ]
    }
  ],
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
}
"""
issue_map = {
    "container-security-context-user-group-id": {"issue_code": "KUBESCORE-W1001"}
}

expected_issues = [
    {
        "issue_code": "container-security-context-user-group-id",
        "issue_text": "Container has no configured security context",
        "location": {
            "path": "workspace/git/myproject/asd.yaml",
            "position": {
                "begin": {"line": 1, "column": 1},
                "end": {"line": 1, "column": 1},
            },
        },
    },
    {
        "issue_code": "container-resources",
        "issue_text": "CPU limit is not set",
        "location": {
            "path": "workspace/git/myproject/asd.yaml",
            "position": {
                "begin": {"line": 1, "column": 1},
                "end": {"line": 1, "column": 1},
            },
        },
    },
]
expected_issues_with_issue_map = [
    {
        "issue_code": "KUBESCORE-W1001",
        "issue_text": "Container has no configured security context",
        "location": {
            "path": "workspace/git/myproject/asd.yaml",
            "position": {
                "begin": {"line": 1, "column": 1},
                "end": {"line": 1, "column": 1},
            },
        },
    },
    {
        "issue_code": "container-resources",
        "issue_text": "CPU limit is not set",
        "location": {
            "path": "workspace/git/myproject/asd.yaml",
            "position": {
                "begin": {"line": 1, "column": 1},
                "end": {"line": 1, "column": 1},
            },
        },
    },
]

WORK_DIR = "/workspace/git/myproject"


@pytest.fixture
def artifact_path(tmp_path: Path) -> str:
    """Creates the uploaded artifact containing SARIF data."""
    artifact_data = {"data": sarif_json, "metadata": {"work_dir": "/"}}

    file_path = tmp_path / "artifact"
    with file_path.open("w") as file:
        json.dump(artifact_data, file)

    return file_path.as_posix()


@pytest.fixture
def issue_map_path(tmp_path: Path) -> str:
    """Creates `issue_map.json` file."""
    file_path = tmp_path / "issue_map.json"
    with file_path.open("w") as file:
        json.dump(issue_map, file)

    return file_path.as_posix()


def test_cli(artifact_path: str, capfd: pytest.CaptureFixture[str]) -> None:
    """Tests `sarif-parser` CLI."""
    cli([artifact_path, "--output=/dev/stdout"])
    out, err = capfd.readouterr()
    assert err == ""

    expected_output = json.dumps(
        {
            "issues": expected_issues,
            "metrics": [],
            "errors": [],
            "is_passed": False,
            "extra_data": {},
        }
    )
    assert out == expected_output


def test_cli_with_issue_map(
    artifact_path: str,
    issue_map_path: str,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Tests `sarif-parser` CLI, with issue code substitution."""
    cli([artifact_path, f"--issue-map-path={issue_map_path}", "--output=/dev/stdout"])
    out, err = capfd.readouterr()
    assert err == ""

    expected_output = json.dumps(
        {
            "issues": expected_issues_with_issue_map,
            "metrics": [],
            "errors": [],
            "is_passed": False,
            "extra_data": {},
        }
    )
    assert out == expected_output


def test_cli_with_invalid_issue_map_path(
    artifact_path: str,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Tests `sarif-parser` CLI, with an invalid issue_map path"""
    cli([artifact_path, "--issue-map-path=some/invalid/path", "--output=/dev/stdout"])
    out, err = capfd.readouterr()
    assert err == ""

    expected_output = json.dumps(
        {
            "issues": expected_issues,  # without issues map since we have passed an invalid path
            "metrics": [],
            "errors": [],
            "is_passed": False,
            "extra_data": {},
        }
    )
    assert out == expected_output


def test_cli_file_not_found() -> None:
    """Tests `sarif-parser` CLI, with issue code substitution."""
    with pytest.raises(FileNotFoundError):
        cli(["/some/doesnotexist.py"])
