# To run: python issue_map_gen.py <directory>#
import json
import os
import sys
from typing import Dict


def generate_json(directory: str) -> None:
    """
    Generate a JSON file containing mappings of issue codes extracted from TOML files in a directory.

    :param directory: The directory containing TOML files with issue codes.
    :type directory: str
    :return: None
    """
    # Dictionary to hold the mappings
    issue_codes: Dict[str, dict] = {}

    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".toml") and filename.startswith("BANDIT-"):
            # Extract the issue code (part after 'CFLIN-' and before '.toml')
            issue_code = filename[len("BANDIT-") : -len(".toml")]

            # Add to the dictionary
            issue_codes[issue_code] = {"issue_code": f"BANDIT-{issue_code}"}

    # Convert dictionary to JSON
    json_data: str = json.dumps(issue_codes, indent=4)

    # Write JSON data to a file in the current directory
    with open("issue_map.json", "w") as file:
        file.write(json_data)
    print("JSON data written to issue_map.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    target: str = sys.argv[1]
    generate_json(target)
