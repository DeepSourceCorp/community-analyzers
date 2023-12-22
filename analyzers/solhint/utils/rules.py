import json
import os
import subprocess
from dataclasses import dataclass
from tempfile import TemporaryDirectory
from typing import Any, Literal

from constants import (
    DEEPSOURCE_SEVERITY_WEIGHT_MAP,
    SOLHINT_CLONE_URL,
    SOLHINT_DOCS_BASE_URL,
    SOLHINT_RULE_CATEGORY_DEEPSOURCE_CATEGORY_MAP,
    SOLHINT_RULE_SEVERITY_CATEGORY_DEEPSOURCE_SEVERITY_MAP,
    SOLHINT_RULES_JSON_FILE,
)

__all__ = ["Rule", "get_all_rules"]


@dataclass
class Rule:
    """
    Represents a Solhint rule.
    """

    rule_id: str
    type: str
    category: Literal[
        "Best Practise Rules", "Security Rules", "Style Guide Rules", "Miscellaneous"
    ]
    description: str
    is_default: bool
    recommended: bool
    deprecated: bool
    severity: Literal["warn", "error"]
    bad_examples: list[dict[str, str]]
    good_examples: list[dict[str, str]]

    @property
    def wiki_url(self) -> str:
        return f"{SOLHINT_DOCS_BASE_URL}/{self.type}/{self.rule_id}.md"

    @property
    def deepsource_category(self) -> str:
        return SOLHINT_RULE_CATEGORY_DEEPSOURCE_CATEGORY_MAP[self.category]

    @property
    def deepsource_severity(self) -> str:
        return SOLHINT_RULE_SEVERITY_CATEGORY_DEEPSOURCE_SEVERITY_MAP[
            (self.severity, self.category)
        ]

    @property
    def deepsource_weight(self) -> int:
        return DEEPSOURCE_SEVERITY_WEIGHT_MAP[self.deepsource_severity]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        meta_data = data["meta"]
        default_setup = meta_data["defaultSetup"]
        severity = "warn"  # default
        if isinstance(default_setup, list):
            if default_setup[0] != "off":
                severity = default_setup[0]
        elif isinstance(default_setup, str) and default_setup != "off":
            severity = default_setup
        docs_data = meta_data["docs"]
        examples_data = docs_data.get("examples", {})

        return cls(
            rule_id=data["ruleId"],
            type=meta_data["type"],
            category=docs_data["category"],
            description=docs_data["description"],
            is_default=meta_data["isDefault"],
            recommended=meta_data["recommended"],
            deprecated=meta_data.get("deprecated", False),
            severity=severity,
            bad_examples=examples_data.get("bad", []),
            good_examples=examples_data.get("good", []),
        )


def dump_rules_as_json() -> None:
    """
    Dumps all Solhint rules into a JSON file.
    """
    clone_command = ["git", "clone", SOLHINT_CLONE_URL, "--depth=1"]
    npm_install = ["npm", "i"]
    print_rules_command = [
        "node",
        "-e",
        'console.log(JSON.stringify(require("./lib/load-rules").loadRules()))',
    ]
    with TemporaryDirectory() as tmpdir:
        subprocess.run(clone_command, cwd=tmpdir, check=True, capture_output=False)
        subprocess.run(
            npm_install, cwd=f"{tmpdir}/solhint", check=True, capture_output=False
        )
        resp = subprocess.run(
            print_rules_command,
            cwd=f"{tmpdir}/solhint",
            check=True,
            capture_output=True,
        )
        with open(SOLHINT_RULES_JSON_FILE, "w") as fp:
            rules_dicts = json.loads(resp.stdout.decode("utf-8"))
            json.dump(json.loads(resp.stdout.decode("utf-8")), fp)
            print(
                f"[+] Dumped {len(rules_dicts)} Solhint rules in {SOLHINT_RULES_JSON_FILE}."
            )


def get_all_rules() -> list[Rule]:
    """
    Returns list of `Rule` objects.
    """
    if not os.path.exists(SOLHINT_RULES_JSON_FILE):
        dump_rules_as_json()
    with open(SOLHINT_RULES_JSON_FILE, "r") as fp:
        rules_dicts = json.load(fp)
        return [Rule.from_dict(rule_dict) for rule_dict in rules_dicts]
