import ast
import json
import os
from textwrap import dedent
from urllib.parse import unquote, urlparse
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Union


def concat_binop(binop: ast.AST) -> str:
    if isinstance(binop, ast.BinOp):
        return concat_binop(binop.left) + concat_binop(binop.right)
    elif isinstance(binop, ast.Constant):
        return binop.value
    return ""


def extract_class_attributes(node: ast.ClassDef) -> Dict[str, Union[str, List[str]]]:
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
    class_data = {}
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_data.update(extract_class_attributes(node))
    return class_data


def extract_page_name(url: str) -> Optional[str]:
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip("/").split("/")
    if path_segments:
        last_segment = os.path.splitext(path_segments[-1])[0]
        page_name = unquote(last_segment.replace("-", " ")).title()
        return page_name.replace("Cfn", "CloudFormation").replace("Cloudformation", "CloudFormation")
    return None


def build_toml(issue: Dict[str, Union[str, List[str]]]) -> str:
    title = issue["shortdesc"]
    description = issue["description"]
    source_url = issue.get("source_url", "")
    tags = issue.get("tags", [])

    content = f"""\
    title = {json.dumps(title).capitalize()}
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
    file_name = f"./issues/CFLIN-{issue['id']}.toml"
    with open(file_name, "w") as file:
        file.write(build_toml(issue))


def extract_attributes_from_directory(directory: str) -> List[Dict[str, Union[str, List[str]]]]:
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
    parser = argparse.ArgumentParser(description="Extract attributes from Python files in a given directory.")
    parser.add_argument("--root_directory", help="Root directory of the cfn-lint repository.")
    args = parser.parse_args()

    directory = Path(args.root_directory)
    path = Path("cfn-lint/src/cfnlint/rules")
    rules_directory = directory / path
    
    attributes_list = extract_attributes_from_directory(rules_directory)
    for attributes in attributes_list:
        write_to_file(attributes)
