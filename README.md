# DeepSource Community Analyzers

Hub of all open-source third-party static analyzers supported by DeepSource. Usage docs can be found at [docs.deepsource.com/docs/community-analyzers](https://docs.deepsource.com/docs/community-analyzers)

## Supported Analyzers

| Analyzer name                                                                 | Latest version | Language / Technology |
| :---------------------------------------------------------------------------- | :------------- | :-------------------- |
| [stackrox/kube-linter](https://github.com/stackrox/kube-linter)               | 0.6.4          | Kubernetes, Helm      |
| [aws-cloudformation/cfn-lint](https://github.com/aws-cloudformation/cfn-lint) | 0.83.3         | AWS CloudFormation    |
| [dart-lang/linter](https://github.com/dart-lang/sdk/tree/main/pkg/linter)     | 3.2.0          | Dart, Flutter         |
| [crytic/slither](https://github.com/crytic/slither)                           | 0.10.0         | Solidity, Vyper       |
| [protofire/solhint](https://github.com/protofire/solhint)                     | 4.1.1          | Solidity              |

---

## Development Guide

### Adding a new analyzer

To add a new analyzer, create a new directory with the analyzer shortcode under the `analyzers` folder.
The following are very important to sync analyzers with DeepSource:

1. `.deepsource/analyzer` directory under `analyzer/<analyzer-shortcode>` directory.

   a. It should contain an `analyzer.toml` file with the following fields:

   - `category`: One of "conf" (Configuration-as-code), "lang" (Language), "covg" (Coverage), "sec" (security)
   - `name`: Name for the Analyzer. Analyzer on DeepSource dashboard and the checks on VCS would show up as this name.
   - `shortcode`: shortcode for the analyzer. This should be same as of the analyzer's directory name. This is the name of the analyzer in the `.deepsource.toml` file.
   - `status`: "active" if analyzer should be live else "draft".
   - `tool_latest_version`: Analyzer's latest version for which issues are synced on DeepSource.
   - `description`: A readable descrioption for this analyzer.

   b. It should contain am `example.toml` file with a snippet to activate this analyzer in `.deepsource.toml` config.

   c. `logo.svg` file.

2. `.deepsource/issues` directory. This contains all issues detected by the analyzer. Each issue's filemane should be `<issue-shortcode>.toml` or `<issue-shortcode.md>` with the following fields:

   - `title`: Title of the issue. No periods are allowed in the title.
   - `category`: Category of the issue. Allowed values are: "bug-risk", "doc", "style", "antipattern", "coverage", "security", "performance", "typecheck", and, "secrets".
   - `description`: Description of the issue. This showld explain the problem in as much detail as possible with possible remediation steps.
   - `severity`: Severity of the issue. Allowed values are: "critical", "major" and "minor".

3. `CI` directory:

Put example configs of all CIs under this directory. These worlflow / CI configs should run the analyzer, create a sarif report and send it to DeepSource.

Each file should be names as `<provider>.<extention>`. Example: `github.yml`, `circleci.yml`, etc.`

4. `utils` directory:

It should contain all the utilities required for the analyzer like issue genrator, issue-map, etc.
For example, please check out `analyzers/kube-linter/utils`.

5. Add a sample sarif report from the analyzer in `tests/fixtures` directory. The file should be named as `<analyzer-shortcode>.sarif`.
   `test_report_parsing` parses all sarif reports under the given directory and checks if the issues are parsed correctly. It is important for that particular test to pass.

### Syncing analyzers and their issues with DeepSource

Push a tag after merging all the changes to the default (master) branch. The `Sync community analyzers` workflow triggers on tag pushes matching `v*` and will sync the analyzers and their issues with DeepSource.

> Note: This action will be done by a member of the DeepSource team; contributors need not create a tag.

### Running tests

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests, and ensure that the coverage report has no missing
  lines.

### The test suite

There are minimal tests for the `run_community_analyzer.py` wrapper in
`tests/test_community_analyzer.py` that do sanity checks, to ensure that the
issue map is being respected, etc.

For the SARIF parser itself, the test suite expects you to create two files in
`sarif-parser/tests/sarif_files`, a SARIF input file with `.sarif` extension,
and the expected DeepSource output file with the same name, but `.sarif.json`
extension.

### Type Checking

Run `mypy .`
