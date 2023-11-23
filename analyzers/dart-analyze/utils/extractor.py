import json
from dataclasses import dataclass
from typing import List
from urllib.request import urlopen


@dataclass
class Issue:
    code: str
    title: str
    description: str
    category: str


class DiagnosticRulesParser:
    def __init__(self, text: str):
        """
        A simple wrapper that parses a diagnostic rules
        from a markdown file.

        Args:
            text (str): The text content to parse
        """
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.pos = 0

    @property
    def exhausted(self):
        """Whether the text content has been exhausted or not."""
        return self.pos >= len(self.lines)

    def next_line(self):
        """Returns the next line to be parsed."""
        return self.lines[self.pos]

    def consume(self):
        """Consumes the current line and moves to the next line."""
        self.pos += 1

    def get_issues(self) -> dict:
        """Parses the the given text and extracts issue definitions."""
        issues = []
        while not self.exhausted:
            line = self.next_line()

            # All issue definitions start with issue code being a
            # heading 3 and the issue code being on that line itself.
            if line.startswith("### "):
                code = line.strip("# \n")
                title = ""
                description = ""
                self.consume()

                # Everything between heading 3 and heading 4
                # is the title of the issue
                while not self.exhausted:
                    line = self.next_line()
                    if line.startswith("#"):
                        break
                    title += line.strip(" \n_") + " "
                    self.consume()
                title = title.strip()
                # Everything after heading 4 to the next heading 3
                # i.e. the next issue definition can be considered
                # to be the issue description
                while not self.exhausted:
                    line = self.next_line()
                    if line.startswith("### "):
                        break
                    if line.startswith("#### Description"):
                        self.consume()
                        continue
                    if "{% prettify dart tag=pre+code %}" in line:
                        line = "```dart"
                    elif "{% endprettify %}" in line:
                        line = "```"
                    description += f"{line}\n"
                    self.consume()
                description = description.strip()

                issues.append(
                    {"code": code, "title": title, "description": description}
                )
            else:
                self.consume()

        return issues


class IssueExtractor:
    LINTER_RULES_URL = (
        "https://github.com/dart-lang/site-www/raw/main/src/_data/linter_rules.json"
    )
    DIAGNOSTIC_RULES_URL = "https://raw.githubusercontent.com/dart-lang/site-www/main/src/tools/diagnostic-messages.md"
    GROUP_CATEGORY_MAP = {
        "style": "antipattern",
        "errors": "bug-risk",
        "pub": "antipattern",
    }

    def __init__(self):
        """
        Extracts dart analyze issues.

        Args:
            directory (str): The directory to use to clone the dart \
                analyze repository
        """
        self._issues = []

    @property
    def issues(self) -> List[Issue]:
        """The list of issues extracted from the dart analyze repository."""
        if len(self._issues) > 0:
            return self._issues

        self._issues = self.fetch_rules()
        return self._issues

    def fetch_rules(self) -> List[Issue]:
        """Fetches all dart analyze rules."""
        return [*self.fetch_linter_rules(), *self.fetch_diagnostic_rules()]

    def fetch_diagnostic_rules(self) -> List[Issue]:
        """Fetches the list of diagnostic rules"""
        response = urlopen(self.DIAGNOSTIC_RULES_URL)
        if response.code != 200:
            raise Exception(f"Failed to fetch diagnostic rules {response.code}")

        rules = DiagnosticRulesParser(response.read().decode()).get_issues()
        return [Issue(**rule, category="bug-risk") for rule in rules]

    def fetch_linter_rules(self) -> List[Issue]:
        """Fetches the list of linter rules."""
        response = urlopen(self.LINTER_RULES_URL)
        if response.code != 200:
            raise Exception(f"Failed to fetch linter rules {response.code}")

        rules = json.load(response)
        return [
            Issue(
                self.get_linter_rule_code(rule),
                self.get_linter_rule_title(rule),
                self.get_linter_rule_description(rule),
                self.get_linter_rule_category(rule),
            )
            for rule in rules
            if rule["state"] == "stable"
        ]

    @classmethod
    def get_linter_rule_code(cls, rule: dict) -> str:
        """Extracts the rule code"""
        return rule["name"]

    @classmethod
    def get_linter_rule_title(cls, rule: dict) -> str:
        """Extract & sanitize the rule title."""
        return rule["description"].rstrip(".").replace('"', r"\"")

    def get_linter_rule_description(cls, rule: dict) -> str:
        """Extracts the description from the rule"""
        return rule["details"]

    @classmethod
    def get_linter_rule_category(cls, rule: dict) -> str:
        """Extracts and returns the category mapped to the rule"""
        return cls.GROUP_CATEGORY_MAP.get(rule["group"])
