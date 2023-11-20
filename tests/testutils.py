import json
import os
from contextlib import contextmanager
from typing import Any, Iterator


def extract_filepaths_from_sarif(
    sarif: dict[str, Any], trim_workdir: bool = False, workdir: str | None = None
) -> list[str]:
    """Extracts filepaths from a SARIF file."""
    filepaths = []
    for run in sarif["runs"]:
        for result in run["results"]:
            filepath = result["locations"][0]["physicalLocation"]["artifactLocation"][
                "uri"
            ]

            if trim_workdir:
                filepath = filepath.replace(workdir, "")

            filepaths.append(filepath)

    return filepaths


def extract_filepaths_from_deepsource_json(
    deepsource_json: dict[str, Any]
) -> list[str]:
    """Extracts filepaths from a DeepSource JSON file."""
    filepaths = []
    for issue in deepsource_json["issues"]:
        filepaths.append(issue["location"]["path"])

    return filepaths


@contextmanager
def temp_analysis_config(
    config_path: str | os.PathLike[str], files: list[str]
) -> Iterator[None]:
    """
    Prepare a minimal analysis config, by only populating `files` field and place it
    in the provided config path.

    Delete the config when the scope of this context manager ends.
    """
    # skipcq: PTC-W6004
    with open(config_path, "w") as file:
        json.dump({"files": files}, file)

    yield

    os.remove(config_path)
