import os

ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "DRT-W"

# The version of the supported tool
VERSION = "stable"  # TODO: change v3.2.0 when tag is officially pushed

ISSUE_MD_TEMPLATE = """---
title: "{title}"
verbose_name: "{verbose_name}"
category: "{category}"
weight: 70
severity: "major"
---
{description}
"""
