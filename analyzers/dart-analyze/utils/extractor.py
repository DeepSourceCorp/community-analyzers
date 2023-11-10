import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from constants import VERSION


@dataclass
class Issue:
    code: str
    title: str
    description: str
    category: str


class IssueExtractor:
    CLONE_URL = "https://github.com/dart-lang/sdk.git"
    RULES_DIRECTORY = "sdk/pkg/linter/lib/src/rules"

    RULE_TITLE_REGEX = re.compile(
        r"const _?desc\s*=\s*([\w\,\.\=\-\+\:\>\<\\\%\!\[\]\{\}\(\)\`\'\"\$\?\@\s\/\\]*);"
    )
    RULE_DESCRIPTION_REGEX = re.compile(
        r"const _?details\s*=\s* r?('''|\"\"\")(.*)('''|\"\"\");", re.S
    )
    RULE_GROUP_REGEX = re.compile(r"group:.*Group\.(.*)(\)\s*;|,)")

    GROUP_CATEGORY_MAP = {
        "style": "antipattern",
        "errors": "bug-risk",
        "pub": "antipattern",
    }

    def __init__(self, directory: str):
        """
        Extracts dart analyze issues.

        Args:
            directory (str): The directory to use to clone the dart \
                analyze repository
        """
        self.clone_directory = Path(directory)
        self._issues = []
        self._clone_repository()

    @property
    def rules_directory(self) -> Path:
        """The directory where the dart analyze rules are defined."""
        return self.clone_directory / self.RULES_DIRECTORY

    @property
    def issues(self) -> List[Issue]:
        """The list of issues extracted from the dart analyze repository."""
        if len(self._issues) > 0:
            return self._issues

        self._issues = []
        for file in self.get_rule_files():
            issue = self.get_issue_from_rule_file(file)
            if issue:
                self._issues.append(issue)

        return self._issues

    def _clone_repository(self) -> None:
        """Clones the dart analyzer repository."""
        commands = (
            f"git clone {self.CLONE_URL} --depth 1 -b {VERSION}",
            f"cd sdk && git checkout {VERSION}",
        )
        for command in commands:
            subprocess.run(
                command,
                cwd=self.clone_directory,
                check=True,
                shell=True,
            )

    def get_rules(self) -> List[str]:
        """Returns the list of rules present in the repository."""
        return [file.stem for file in self.get_rule_files()]

    def get_rule_files(self) -> List[Path]:
        """Returns a list of file paths of the rule files."""
        extracted_files = []

        for curr_dir, _, files in os.walk(self.rules_directory):
            for file in files:
                extracted_files.append(Path(curr_dir) / file)

        return extracted_files

    def get_rule_title(self, contents: str) -> str | None:
        """
        Extracts the title of the rule from the file contents.

        Args:
            contents (str): The rule file contents.
        """
        CHARS_TO_STRIP = "'\" "
        CHARS_TO_LSTRIP = "r"

        match = self.RULE_TITLE_REGEX.search(contents)
        if not match:
            return None

        title_parts = match.group(1).split("\n")
        sanitized_parts = []
        for part in title_parts:
            sanitized_parts.append(part.lstrip(CHARS_TO_LSTRIP).strip(CHARS_TO_STRIP))

        return " ".join(sanitized_parts)

    def get_rule_description(self, contents: str) -> str | None:
        """
        Extracts the description of the rule from the file contents.

        Args:
            contents (str): The rule file contents.
        """
        if match := self.RULE_DESCRIPTION_REGEX.search(contents):
            return match.group(2).strip()

        return None

    def get_rule_category(self, contents: str) -> None:
        """

        Extracts the category of the rule from the file contents.

        Args:
            contents (str): The rule file contents.
        """
        if match := self.RULE_GROUP_REGEX.search(contents):
            group = match.group(1)
            return self.GROUP_CATEGORY_MAP.get(group)

        return None

    def get_issue_from_rule_file(self, file: Path) -> Issue | None:
        """
        Extracts an issue from the given rule file.
        """
        with file.open() as f:
            contents = f.read()

        title = self.get_rule_title(contents)
        if not title:
            print(f"[{file.name}] Failed to extract title")

        description = self.get_rule_description(contents)
        if not description:
            print(f"[{file.name}] Failed to extract description")
            return None

        if title is None:
            print(f"[{file.name}] Setting title from description")
            title = description.split("\n")[0]

        category = self.get_rule_category(contents)
        if not category:
            print(f"[{file.name}] Failed to extract category")
            return None

        return Issue(
            code=file.stem, title=title, description=description, category=category
        )
