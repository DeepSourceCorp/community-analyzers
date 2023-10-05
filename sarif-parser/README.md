# sarif-parser

Parse SARIF reports and covert them to DeepSource issues.

## Usage

```bash
git clone https://github.com/DeepSourceCorp/community-analyzers
cd community-analyzers/sarif-parser
# to install the package
pip install .
# to convert a single sarif file to DeepSource JSON
sarif-parser path/to/sarif-file.json --output /dev/stdout
# to convert a folder containing ONLY sarif files, to DeepSource JSON.
# output defaults to <TOOLBOX_PATH>/analysis_results.json
sarif-parser path/to/folder
```

## Local Development / Testing

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests, and ensure that the coverage report has no missing
  lines.

### The test suite

The test suite expects you to create two files in `tests/sarif_files`, a SARIF
input file with `.sarif` extension, and the expected DeepSource output file
with the same name, but `.sarif.json` extension.

## Type Checking

Run `mypy .`
