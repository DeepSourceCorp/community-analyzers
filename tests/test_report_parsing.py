import json
import os
import tempfile
import tomllib as toml
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Set

import frontmatter  # type: ignore[import-untyped]

import run_community_analyzer


def make_artifact(report_path: str, workdir: str = "") -> str:
    """Return an artifact file for the given report, with the given workdir."""
    artifact_path = tempfile.NamedTemporaryFile().name
    # skipcq: PTC-W0064  # Report path is safe
    with open(report_path) as report_file:
        data = report_file.read()
    with open(artifact_path, "w") as artifact_file:
        json.dump({"data": data, "metadata": {"work_dir": workdir}}, artifact_file)
    return artifact_path


@contextmanager
def parse_single_artifact(
    report_path: str, report_name: str
) -> Iterator[Dict[str, Any]]:
    """Run community analyzer on a single artifact and return the deepsource result object."""
    artifact_path = make_artifact(report_path)
    toolbox_path = tempfile.gettempdir()
    os.environ["ARTIFACTS_PATH"] = artifact_path
    os.environ["TOOLBOX_PATH"] = toolbox_path
    output_path = Path(toolbox_path, "analysis_results.json").as_posix()
    run_community_analyzer.main([f"--analyzer={report_name}"])
    with open(output_path) as output_file:
        yield json.load(output_file)

    os.remove(artifact_path)
    os.remove(output_path)


def get_issue_codes_for_tool(report_tool: str) -> Set[str]:
    """Return a set of valid issue codes for the given report tool."""
    issues = set()
    issues_dir_path = Path.joinpath(
        Path(__file__).parent.parent, f"analyzers/{report_tool}/.deepsource/issues"
    ).as_posix()
    for issue_file in os.listdir(issues_dir_path):
        issue_code, ext = issue_file.split(".", 1)
        if ext == "toml":
            parser = toml
        else:
            parser = frontmatter
        issue_file_path = os.path.join(issues_dir_path, issue_file)
        with open(issue_file_path) as fp:
            issue_data = parser.loads(fp.read())
            archived = issue_data.get("archived", False)
            if not archived:
                issues.add(issue_code)

    return issues


def test_sarif_parser() -> None:
    """End to end test to make sure the SARIF parser throws no errors while parsing reports."""
    # We parse all reports in `tests/fixtures/reports` and try to make a deepsource report out of it.
    # There shouldn't be any errors while parsing the reports.
    # All test reports are present in the `tests/fixtures/reports` directory.
    reports_base_dir = Path.joinpath(Path(__file__).parent, "fixtures", "reports")
    reports = os.listdir(reports_base_dir)
    for report in reports:
        report_tool = report.removesuffix(".sarif")
        active_issues = get_issue_codes_for_tool(report_tool)
        report_path = Path(reports_base_dir, report).as_posix()

        with parse_single_artifact(report_path, report_tool) as result:
            missing_ids = []
            assert result
            assert result["issues"] is not None
            for issue in result["issues"]:
                issue_code = issue["issue_code"]
                if issue_code not in active_issues:
                    missing_ids.append(issue_code)

            if missing_ids:
                raise AssertionError(
                    f"{report_tool} report has {len(missing_ids)} missing issue "
                    f"code(s): {', '.join(missing_ids)}\n"
                    "Please make sure you add issue files for these issue codes in the "
                    "respective issues directory."
                )
