import os

ISSUE_MAP_FILE = os.path.join(os.path.dirname(__file__), "issue_map.json")
ISSUE_PREFIX = "DRT-W"


ISSUE_TOML_TEMPLATE = """
title = "{title}"
weight = 70
severity = "major"
category = "{category}"
verbose_name = "{verbose_name}"
description = '''
{description}
'''
"""
