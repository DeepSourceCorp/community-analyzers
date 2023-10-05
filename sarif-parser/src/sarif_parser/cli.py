"""CLI interface for sarif_parser."""
import argparse
import json
import os.path

import sarif_parser

TOOLBOX_PATH = os.getenv("TOOLBOX_PATH", "/toolbox")
OUTPUT_PATH = os.path.join(TOOLBOX_PATH, "analysis_results.json")


class SarifParserArgs:
    filepath: str
    output: str
    issue_map_path: str


def cli(argv: list[str] | None = None) -> None:
    """CLI interface."""
    parser = argparse.ArgumentParser("sarif_parser")
    parser.add_argument("filepath", help="Path to artifact containing SARIF data")
    parser.add_argument("--issue-map-path", help="JSON file for replacing issue codes.")
    parser.add_argument("--output", help="Path for writing analysis results.")
    args = parser.parse_args(argv, namespace=SarifParserArgs)

    filepath = args.filepath
    if not os.path.exists(filepath):
        raise RuntimeError(f"{filepath} does not exist.")

    target_path = args.output
    if target_path is None:
        target_path = OUTPUT_PATH

    if os.path.isdir(filepath):
        artifacts = [os.path.join(filepath, file) for file in os.listdir(filepath)]
    else:
        artifacts = [filepath]

    deepsource_issues = []
    for filepath in artifacts:
        with open(filepath) as file:  # skipcq: PTC-W6004 -- nothing sensitive here
            artifact = json.load(file)

        sarif_data = json.loads(artifact["data"])
        work_dir = artifact["metadata"]["work_dir"]
        issues = sarif_parser.parse(sarif_data, work_dir, args.issue_map_path)
        deepsource_issues.extend(issues)

    issues_dict = {
        "issues": deepsource_issues,
        "metrics": [],
        "errors": [],
        "is_passed": True if not deepsource_issues else False,
        "extra_data": {},
    }
    with open(target_path, "w") as file:
        json.dump(issues_dict, file)
