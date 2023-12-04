import argparse
import json
import logging
import os
import os.path

from sarif_parser import run_sarif_parser

import sentry

sentry.initialize()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)


class CommunityAnalyzerArgs:
    """Arguments for the community analyzer."""

    analyzer: str


def get_issue_map(analyzer_name: str) -> str:
    """Returns the appropriate issue map filepath for the given analyzer."""
    analyzers_dir = os.path.join(os.path.dirname(__file__), "analyzers")
    return os.path.join(analyzers_dir, analyzer_name, "utils", "issue_map.json")


def get_files_to_analyze(code_path: str) -> set[str]:
    """
    Read the analysis config to get the list of files to analyze.
    Always raise issues only in these files.
    """
    toolbox_path = os.getenv("TOOLBOX_PATH", "/toolbox")
    analysis_config_path = os.path.join(toolbox_path, "analysis_config.json")

    if not os.path.exists(analysis_config_path):
        raise ValueError(f"Could not find analysis config at {analysis_config_path}.")

    with open(analysis_config_path) as file:
        analysis_config = json.load(file)

    logger.info("Files in analysis config: %s", analysis_config["files"])
    return {
        os.path.relpath(analysis_file, code_path)
        for analysis_file in analysis_config["files"]
    }


def main(argv: list[str] | None = None) -> None:
    """Runs the CLI."""
    code_path = os.getenv("CODE_PATH", "/code")
    toolbox_path = os.getenv("TOOLBOX_PATH", "/toolbox")
    output_path = os.path.join(toolbox_path, "analysis_results.json")
    artifacts_path = os.getenv("ARTIFACTS_PATH", "/artifacts")

    parser = argparse.ArgumentParser("sarif_parser")
    parser.add_argument(
        "--analyzer",
        help="Which community analyzer to run. Example: 'kube-linter'",
        required=True,
    )
    args = parser.parse_args(argv, namespace=CommunityAnalyzerArgs)

    analyzer_name = args.analyzer
    issue_map_path = get_issue_map(analyzer_name)
    modified_files = get_files_to_analyze(code_path)
    run_sarif_parser(
        artifacts_path, output_path, issue_map_path, modified_files=modified_files
    )


if __name__ == "__main__":
    main()  # pragma: no cover
