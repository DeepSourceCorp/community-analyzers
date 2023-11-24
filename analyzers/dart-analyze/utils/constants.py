import os

ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "DRT-W"


ISSUE_TOML_TEMPLATE = '''
title = "{title}"
verbose_name = "{verbose_name}"
category = "{category}"
severity = "major"
weight = 70
description = """
{description}
"""
'''
