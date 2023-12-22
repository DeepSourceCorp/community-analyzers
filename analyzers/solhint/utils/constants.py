import os

__all__ = [
    "SOLHINT_CLONE_URL",
    "SOLHINT_DOCS_BASE_URL",
    "SOLHINT_RULES_JSON_FILE",
    "ISSUE_MAP_FILE",
    "ISSUES_DIR",
    "ISSUE_PREFIX",
    "DEEPSOURCE_SEVERITY_WEIGHT_MAP",
    "SOLHINT_RULE_SEVERITY_CATEGORY_DEEPSOURCE_SEVERITY_MAP",
    "SOLHINT_RULE_CATEGORY_DEEPSOURCE_CATEGORY_MAP",
]

SOLHINT_CLONE_URL = "https://github.com/protofire/solhint.git"
SOLHINT_DOCS_BASE_URL = "https://github.com/protofire/solhint/blob/develop/docs/rules"

# path to the `solhint_rules.json` located in the same directory as this script
SOLHINT_RULES_JSON_FILE = os.path.join(os.path.dirname(__file__), "solhint_rules.json")
# path to the `issue_map.json` located in the same directory as this script
ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
# path to the `.deepsource/issues/` directory located in the parent directory of this script
ISSUES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".deepsource/issues"
)

ISSUE_PREFIX = "SOLHINT-W"

DEEPSOURCE_SEVERITY_WEIGHT_MAP = {
    "minor": 40,
    "major": 60,
    "critical": 80,
}

SOLHINT_RULE_SEVERITY_CATEGORY_DEEPSOURCE_SEVERITY_MAP = {
    ("warn", "Best Practise Rules"): "minor",
    ("warn", "Miscellaneous"): "minor",
    ("warn", "Security Rules"): "major",
    ("warn", "Style Guide Rules"): "minor",
    ("error", "Best Practise Rules"): "major",
    ("error", "Miscellaneous"): "major",
    ("error", "Security Rules"): "critical",
    ("error", "Style Guide Rules"): "major",
}

SOLHINT_RULE_CATEGORY_DEEPSOURCE_CATEGORY_MAP = {
    "Best Practise Rules": "antipattern",
    "Miscellaneous": "antipattern",
    "Security Rules": "security",
    "Style Guide Rules": "style",
}
