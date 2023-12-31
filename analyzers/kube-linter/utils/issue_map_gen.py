import itertools
import json
import os
import subprocess

# path to the `issue_map.json` located in the same directory as this script
ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "KUBELIN-W"


def get_issues_json() -> list:
    """Return a list of issues from kubelinter."""
    # run kubelinter to get the list of checks in the json format
    cmd = "kube-linter checks list --format json".split()
    resp = subprocess.run(cmd, capture_output=True, check=True)
    return json.loads(resp.stdout.decode("utf-8"))


def get_next_code(mapping) -> str:
    """Return the next available issue code."""
    num_issues = len(mapping.keys())  # get the number of issues already in the mapping
    next_code = 1001 + num_issues  # issue code series starts from `1001`
    yield from itertools.count(next_code)


def get_issue_map() -> dict:
    """Return the issue map."""
    with open(ISSUE_MAP_FILE, "r") as f:
        return json.load(f)


def generate_mapping() -> None:
    """Generate a mapping of DeepSource assigned issue codes to issue names."""
    # Example mapping:
    # {
    #     "container-privileged": {"issue_code": "KUBELIN-W1001"},
    # }
    issue_map = get_issue_map()
    generate_code = get_next_code(issue_map)

    kubelinter_cli_issues = get_issues_json()
    if len(kubelinter_cli_issues) > len(issue_map):
        # if the number of issues in the mapping is less than the number of issues in the cli,
        # then generate the mapping for the new issues
        for issue in kubelinter_cli_issues:
            if issue["name"] not in issue_map.keys():
                next_code = next(generate_code)
                issue_map[issue["name"]] = {"issue_code": f"{ISSUE_PREFIX}{next_code}"}

        with open(ISSUE_MAP_FILE, "w") as f:
            json.dump(issue_map, f, indent=4)
