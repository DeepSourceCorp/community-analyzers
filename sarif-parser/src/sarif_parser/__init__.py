"""sarif-parser - Parse SARIF reports and covert them to DeepSource issues."""
from __future__ import annotations

import json
from typing import Any, TypedDict


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
    issue_map_path: str | None = None,
) -> list[Issue]:
    """Parses a SARIF file and returns a list of DeepSource issues."""
    deepsource_issues: list[Issue] = []

    if issue_map_path is not None:
        with open(issue_map_path) as file:
            issue_map = json.load(file)
    else:
        issue_map = {}

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
            if issue_code in issue_map:
                issue_code = issue_map[issue_code]["issue_code"]

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
