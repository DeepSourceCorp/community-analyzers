import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Dict, Any

import run_community_analyzer


def make_artifact(report_path: str, workdir: str="") -> str:
    """Return an artifact file for the given report, with the given workdir."""
    artifact_path = tempfile.NamedTemporaryFile().name
    # skipcq: PTC-W0064  # Report path is safe
    with open(report_path) as report_file:
        data = report_file.read()
    with open(artifact_path, "w") as artifact_file:
        json.dump({'data': data, 'metadata': {'work_dir': workdir}}, artifact_file)
    return artifact_path


@contextmanager
def parse_single_artifact(report_path: str, report_name: str) -> Iterator[Dict[str, Any]]:
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


def test_sarif_parser() -> None:
    """End to end test to make sure the SARIF parser throws no errors while parsing reports."""
    # We parse all reports in `tests/fixtures/reports` and try to make a deepsource report out of it.
    # There shouldn't be any errors while parsing the reports.
    # All test reports are present in the `tests/fixtures/reports` directory.
    reports_base_dir = Path.joinpath(Path(__file__).parent, "fixtures", "reports")
    reports = os.listdir(reports_base_dir)
    for report in reports:
        report_tool = report.removesuffix(".sarif")
        report_path = Path(reports_base_dir, report).as_posix()
        with parse_single_artifact(report_path, report_tool) as result:
            assert result
            assert result["issues"] is not None
