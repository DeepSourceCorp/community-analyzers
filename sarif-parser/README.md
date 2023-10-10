# sarif-parser

Parse SARIF reports and covert them to DeepSource issues.

## Usage

```bash
git clone https://github.com/DeepSourceCorp/community-analyzers
cd community-analyzers/sarif-parser
# to install the package
pip install .
# to convert a single sarif file to DeepSource JSON, and output to terminal
sarif-parser path/to/sarif-file.json --output /dev/stdout
# to convert a folder containing ONLY sarif files, to DeepSource JSON.
# output defaults to <TOOLBOX_PATH>/analysis_results.json
sarif-parser path/to/folder
```
