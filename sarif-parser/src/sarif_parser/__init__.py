"""sarif-parser - Parse SARIF reports and covert them to DeepSource issues."""
from __future__ import annotations

import hashlib
import json
import os.path
from typing import Any, TypedDict, Union, Sequence

import sentry


class Issue(TypedDict):
    issue_code: str
    issue_text: str
    location: IssueLocation


class IssueLocation(TypedDict):
    path: str
    position: IssuePosition


class IssuePosition(TypedDict):
    begin: LineColumn
    end: LineColumn


class LineColumn(TypedDict):
    line: int
    column: int

def parse(
    sarif_data: dict[str, Any],
    work_dir: str = "",
    issue_map: dict[str, Any] | None = None,
) -> list[Issue]:
    """Parses a SARIF file and returns a list of DeepSource issues."""
    if issue_map is None:
        issue_map = {}

    deepsource_issues: list[Issue] = []
    for run in sarif_data["runs"]:
        for issue in run["results"]:
            assert len(issue["locations"]) == 1
            location = issue["locations"][0]["physicalLocation"]
            issue_path = location["artifactLocation"]["uri"]
            # remove file:// prefix if present
            issue_path = issue_path.removeprefix("file://")
            # remove work_dir prefix, if present
            issue_path = issue_path.removeprefix(work_dir)
            # remove leading "/" if any
            issue_path = issue_path.removeprefix("/")

            start_line = location.get("contextRegion", {}).get(
                "startLine"
            ) or location.get("region", {}).get("startLine")
            start_column = (
                location.get("contextRegion", {}).get("startColumn")
                or location.get("region", {}).get("startColumn")
                or 1  # columns are 1 indexed by default
            )
            end_line = (
                location.get("contextRegion", {}).get("endLine")
                or location.get("region", {}).get("endLine")
                or start_line
            )
            end_column = (
                location.get("contextRegion", {}).get("endColumn")
                or location.get("region", {}).get("endColumn")
                or start_column
            )

            issue_code = issue["ruleId"]
            if issue_map and issue_code in issue_map:
                issue_code = issue_map[issue_code]["issue_code"]
            else:
                # This issue isn't sanitised. Send an alert.
                sentry.raise_info(
                    f"Could not find issue code for rule {issue_code} in issue map.",
                    context= {
                        "tool": run.get("tool", {}).get("driver", {}).get("name"),
                        "version": run.get("tool", {}).get("driver", {}).get("version"),
                        }
                )

            deepsource_issue = Issue(
                issue_code=issue_code,
                issue_text=issue["message"]["text"],
                location=IssueLocation(
                    path=issue_path,
                    position=IssuePosition(
                        begin=LineColumn(line=start_line, column=start_column),
                        end=LineColumn(line=end_line, column=end_column),
                    ),
                ),
            )
            deepsource_issues.append(deepsource_issue)

    return deepsource_issues


def results_hash(sarif_data: dict[str, Any]) -> str:
    """Returns a hash of the results in the SARIF file."""
    # Extract results from SARIF daa. We take hash only for results.
    run_results = {}
    for idx, result in enumerate(sarif_data["runs"]):
        run_results[idx] = result["results"]
    results_str = json.dumps(run_results, sort_keys=True)

    # Calculate a checksum of the results
    return hashlib.sha256(results_str.encode(), usedforsecurity=False).hexdigest()


def run_sarif_parser(
    filepath: Union[str, os.PathLike[str]],
    output_path: Union[str, os.PathLike[str]],
    issue_map_path: str | None,
) -> None:
    """Parse SARIF files from given filepath, and save JSON output in output path."""
    # Get list of sarif files
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} does not exist.")

    if os.path.isdir(filepath):
        # Get list of files in directory, sorted by name in the reversed order
        artifacts: Sequence[str | os.PathLike[str]] = sorted(
            (os.path.join(filepath, file) for file in os.listdir(filepath)),
            reverse=True,
        )
    else:
        artifacts = [filepath]

    # Prepare mapping from SARIF rule IDs to DeepSource issue codes
    issue_map = None
    if issue_map_path:
        try:
            with open(issue_map_path) as file:
                issue_map = json.load(file)
        except FileNotFoundError:
            # It is not mandatory for an analyzer to have an issue map.
            # But, log this as an info.
            sentry.raise_info(
                f"Could not find issue map at {issue_map_path} for analyzer."
            )

    # Run parser
    deepsource_issues = []
    artifact_hashes = set()
    for artifact_path in artifacts:
        with open(artifact_path) as file:  # skipcq: PTC-W6004 -- nothing sensitive here
            artifact = json.load(file)

        sarif_data = json.loads(artifact["data"])
        sarif_hash = results_hash(sarif_data)

        if sarif_hash in artifact_hashes:
            # Skip this artifact, as it is a duplicate
            continue
        else:
            artifact_hashes.add(sarif_hash)

        work_dir = artifact["metadata"]["work_dir"]
        issues = parse(sarif_data, work_dir, issue_map)
        deepsource_issues.extend(issues)

    issues_dict = {
        "issues": deepsource_issues,
        "metrics": [],
        "errors": [],
        "is_passed": len(deepsource_issues) == 0,
        "extra_data": {},
    }
    with open(output_path, "w") as file:
        json.dump(issues_dict, file)
