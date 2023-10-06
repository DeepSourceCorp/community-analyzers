# DeepSource Community Analyzers

Hub of all open-sourced third-party static analyzers supported by DeepSource.

## Supported Analyzers

| Analyzer name                                                   | Latest version | Language / Technology  |
| :-------------------------------------------------------------- | :------------- | :--------------------- |
| [facebook/infer](https://github.com/facebook/infer)             | v1.1.0         | Java, C++, Objective-C |
| [Azure/bicep](https://github.com/Azure/bicep)                   | v0.20.4        | Azure Resource Manager |
| [stackrox/kube-linter](https://github.com/stackrox/kube-linter) | 0.6.4          | Kubernetes, Helm       |

---

## Development Guide

### Running tests

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests, and ensure that the coverage report has no missing
  lines.

### The test suite

There are minimal tests for the `run_community_analyzer.py` wrapper in
`tests/community_analyzer_test.py` that do sanity checks, to ensure that the
issue map is being respected, etc.

For the SARIF parser itself, the test suite expects you to create two files in
`sarif-parser/tests/sarif_files`, a SARIF input file with `.sarif` extension,
and the expected DeepSource output file with the same name, but `.sarif.json`
extension.

### Type Checking

Run `mypy .`

## Maintenance Guide

...
