import json
import os
import pathlib
import shutil
from contextlib import contextmanager
from typing import Any, Dict, Iterator

import run_community_analyzer


@contextmanager
def patch_env_values(
    toolbox_path: pathlib.Path, artifacts_path: pathlib.Path
) -> Iterator[None]:
    """Context manager to patch the ARTIFACTS_PATH environment variable"""
    old_artifacts_path = os.getenv("ARTIFACTS_PATH")
    old_toolbox_path = os.getenv("TOOLBOX_PATH")
    os.environ["ARTIFACTS_PATH"] = str(artifacts_path)
    os.environ["TOOLBOX_PATH"] = str(toolbox_path)
    try:
        yield
    finally:
        os.environ["ARTIFACTS_PATH"] = old_artifacts_path or ""
        os.environ["TOOLBOX_PATH"] = old_toolbox_path or ""


def freeze_dict(unfrozen: Dict[str, Any]) -> frozenset[tuple[str, object] | object]:
    """Recursively freeze a dictionary."""
    return frozenset(
        (key, freeze_dict(value) if isinstance(value, dict) else value)
        for key, value in unfrozen.items()
    )


def test_duplicate_artifacts(tmp_path: pathlib.Path) -> None:
    """Make sure results are not duplicated when same artifacts are reported more than"""
    # create a temporary directory to store duplicate artifacts
    toolbox_path = tmp_path / "toolbox"
    artifacts_dir = tmp_path / "artifacts"
    toolbox_path.mkdir()
    artifacts_dir.mkdir()

    # Copy the artifact from `./test_artifacts` to the temporary directory
    artifact_path = pathlib.Path(__file__).parent / "test_artifacts" / "kubelinter_1"
    shutil.copy(artifact_path, artifacts_dir / "artifact_1")
    shutil.copy(artifact_path, artifacts_dir / "artifact_2")
    shutil.copy(artifact_path, artifacts_dir / "artifact_3")

    # Run the community analyzer on the artifact directory
    with patch_env_values(toolbox_path, artifacts_dir):
        run_community_analyzer.main(["--analyzer=kube-linter"])

    # Make sure there are no duplicates in the results
    with open(toolbox_path / "analysis_results.json") as fp:
        analysis_results = json.load(fp)
        issues_raised = analysis_results["issues"]

    issues_set = {freeze_dict(issue) for issue in issues_raised}

    # assert that all the issues raised are unique
    assert len(issues_raised) == len(issues_set)
    # Make sure the issues are same
    for issue in issues_raised:
        assert freeze_dict(issue) in issues_set
