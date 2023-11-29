import os
import json
import sys

def generate_json(directory):
    # Dictionary to hold the mappings
    issue_codes = {}

    # Iterate through each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".toml") and filename.startswith("CFLIN-"):
            # Extract the issue code (part after 'CFLIN-' and before '.toml')
            issue_code = filename[len("CFLIN-"):-len(".toml")]
            
            # Add to the dictionary
            issue_codes[issue_code] = {"issue_code": f"CFLIN-{issue_code}"}

    # Convert dictionary to JSON
    json_data = json.dumps(issue_codes, indent=4)

    # Write JSON data to a file in the current directory
    with open("issue_map.json", "w") as file:
        file.write(json_data)
    print("JSON data written to issue_map.json")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    generate_json(directory)
