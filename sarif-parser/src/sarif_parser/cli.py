"""CLI interface for sarif_parser."""
import argparse

from sarif_parser import run_sarif_parser


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
    run_sarif_parser(args.filepath, args.output, args.issue_map_path)
