# To run: python issue_gen.py --root_directory=<parent directory of cfn-lint>
import argparse
import ast
import json
import os
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional, Union
from urllib.parse import unquote, urlparse


def concat_binop(binop: ast.AST) -> str:
    """
    Recursively concatenate binary operation nodes into a single string.

    Args:
        binop (ast.AST): Binary operation node.

    Returns:
        str: Concatenated string.
    """
    if isinstance(binop, ast.BinOp):
        return concat_binop(binop.left) + concat_binop(binop.right)
    if isinstance(binop, ast.Constant):
        return binop.value
    return ""


def extract_class_attributes(node: ast.ClassDef) -> Dict[str, Union[str, List[str]]]:
    """
    Extract class attributes from a ClassDef node in an abstract syntax tree.

    Args:
        node (ast.ClassDef): ClassDef node.

    Returns:
        Dict[str, Union[str, List[str]]]: Extracted class attributes.
    """
    class_data = {}
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if target.id in ["id", "shortdesc", "description", "source_url"]:
                    class_data[target.id] = concat_binop(item.value)
                elif target.id == "tags":
                    class_data["tags"] = [
                        concat_binop(element) for element in item.value.elts
                    ]
    return class_data


def extract_attributes_from_code(code: str) -> Dict[str, Union[str, List[str]]]:
    """
    Extract attributes from Python code.

    Args:
        code (str): Python code as a string.

    Returns:
        Dict[str, Union[str, List[str]]]: Extracted attributes.
    """
    class_data = {}
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_data.update(extract_class_attributes(node))
    return class_data


def extract_page_name(url: str) -> Optional[str]:
    """
    Extract the page name from a URL.

    Args:
        url (str): Input URL.

    Returns:
        Optional[str]: Extracted page name or None if not found.
    """
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip("/").split("/")
    if path_segments:
        last_segment = os.path.splitext(path_segments[-1])[0]
        page_name = unquote(last_segment.replace("-", " ")).title()
        return page_name.replace("Cfn", "CloudFormation").replace(
            "Cloudformation", "CloudFormation"
        )
    return None


def build_toml(issue: Dict[str, Union[str, List[str]]]) -> str:
    """
    Build a TOML string from issue data.

    Args:
        issue (Dict[str, Union[str, List[str]]]): Issue data.

    Returns:
        str: TOML string.
    """
    title = issue["shortdesc"]
    description = issue["description"]
    source_url = issue.get("source_url", "")
    tags = issue.get("tags", [])

    content = f"""\
    title = {json.dumps(title).capitalize()}
    verbose_name = "{issue["id"]}"
    severity = "major"
    category = "antipattern"
    weight = 70
    tags = [{", ".join([json.dumps(tag) for tag in tags])}]
    description = '''
    {description}

    ### References:
    [{extract_page_name(source_url)}]({source_url})
    '''
    """
    return dedent(content)


def write_to_file(issue: Dict[str, Union[str, List[str]]]) -> None:
    """
    Write issue data to a TOML file.

    Args:
        issue (Dict[str, Union[str, List[str]]]): Issue data.
    """
    file_name = f"./issues/CFLIN-{issue['id']}.toml"
    with open(file_name, "w") as file:
        file.write(build_toml(issue))


def extract_attributes_from_directory(
    directory: str,
) -> List[Dict[str, Union[str, List[str]]]]:
    """
    Extract attributes from Python files in a directory.

    Args:
        directory (str): Root directory to search for Python files.

    Returns:
        List[Dict[str, Union[str, List[str]]]]: List of extracted attributes.
    """
    all_classes_data = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        code = f.read()
                        class_data = extract_attributes_from_code(code)
                        if class_data:
                            all_classes_data.append(class_data)
                    except Exception as e:
                        print(f"Error parsing file {file}: {e}")
    return all_classes_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract attributes from Python files in a given directory."
    )
    parser.add_argument(
        "--root_directory", help="Root directory of the cfn-lint repository."
    )
    args = parser.parse_args()

    base = Path(args.root_directory)
    path = Path("cfn-lint/src/cfnlint/rules")
    rules_directory = base / path

    attributes_list = extract_attributes_from_directory(rules_directory)
    for attributes in attributes_list:
        write_to_file(attributes)
