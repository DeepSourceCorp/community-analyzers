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


class IssueExtractor:
    ISSUES_URL = (
        "https://github.com/dart-lang/site-www/raw/main/src/_data/linter_rules.json"
    )
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

        rules = self.fetch_rules()
        self._issues = [
            Issue(
                self.get_code(rule),
                self.get_title(rule),
                self.get_description(rule),
                self.get_category(rule),
            )
            for rule in rules
            if rule["state"] == "stable"
        ]

        return self._issues

    def fetch_rules(self) -> dict:
        """Fetches the list of issues."""
        response = urlopen(self.ISSUES_URL)
        if response.code != 200:
            raise Exception(f"Failed to fetch rules {response.code}")

        return json.loads(response.read())

    @classmethod
    def get_code(cls, rule: dict) -> str:
        """Extracts the rule code"""
        return rule["name"]

    @classmethod
    def get_title(cls, rule: dict) -> str:
        """Extract & sanitize the rule title."""
        return rule["description"].rstrip(".").replace('"', r"\"")

    def get_description(cls, rule: dict) -> str:
        """Extracts the description from the rule"""
        return rule["details"]

    @classmethod
    def get_category(cls, rule: dict) -> str:
        """Extracts and returns the category mapped to the rule"""
        return cls.GROUP_CATEGORY_MAP.get(rule["group"])
