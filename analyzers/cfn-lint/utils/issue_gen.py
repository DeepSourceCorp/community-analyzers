import os
import ast
import json
from textwrap import dedent
from urllib.parse import urlparse, unquote


def concat_binop(binop):
    """
    Concatenate the values of binary operations in AST.

    Args:
    - binop (ast.BinOp): Binary operation node from AST

    Returns:
    - str: Concatenated value of binary operation
    """
    if isinstance(binop, ast.BinOp):
        return concat_binop(binop.left) + concat_binop(binop.right)
    elif isinstance(binop, ast.Constant):
        return binop.value
    return ""


def extract_class_attributes(node):
    """
    Extract specific attributes from a class node in AST.

    Args:
    - node (ast.ClassDef): Class definition node in AST

    Returns:
    - dict: Extracted attributes from class
    """
    class_data = {}
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if target.id in ["id", "shortdesc", "description", "source_url"]:
                    class_data[target.id] = concat_binop(item.value)
                elif target.id == "tags":
                    class_data["tags"] = [concat_binop(element) for element in item.value.elts]
    return class_data


def extract_attributes_from_code(code):
    """
    Extract specific attributes from a class in the provided code.

    Args:
    - code (str): Source code to extract data from

    Returns:
    - dict: Extracted attributes from class in code
    """
    class_data = {}
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_data.update(extract_class_attributes(node))
    return class_data


def extract_page_name(url):
    """
    Extract and format the page name from a given URL.

    Args:
    - url (str): URL to extract page name from

    Returns:
    - str: Formatted page name
    """
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    if path_segments:
        last_segment = os.path.splitext(path_segments[-1])[0]
        page_name = unquote(last_segment.replace('-', ' ')).title()
        page_name = page_name.replace('Cfn', 'CloudFormation')
        page_name = page_name.replace('Cloudformation', 'CloudFormation')
        return page_name
    return None


def build_toml(issue):
    """
    Build a TOML string from issue data.

    Args:
    - issue (dict): Issue data

    Returns:
    - str: Issue data in TOML format
    """
    title = issue["shortdesc"]
    description = issue["description"]
    source_url = issue.get("source_url", "")
    tags = issue.get("tags", [])

    content = f"""\
    title = {json.dumps(title)}
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


def write_to_file(issue):
    """
    Write issue data to a TOML file.

    Args:
    - issue (dict): Issue data
    """
    file_name = f"./issues/CFLIN-{issue['id']}.toml"
    with open(file_name, "w") as file:
        file.write(build_toml(issue))


def extract_attributes_from_directory(directory):
    """
    Extract class attributes from all Python files in a given directory.

    Args:
    - directory (str): Directory path to extract attributes from

    Returns:
    - list: List of dictionaries with extracted class attributes
    """
    all_classes_data = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        code = f.read()
                        class_data = extract_attributes_from_code(code)
                        if class_data:
                            all_classes_data.append(class_data)
                    except Exception as e:
                        print(f"Error parsing file {file}: {e}")

    return all_classes_data


if __name__ == "__main__":
    base_directory = "/Users/vishnu/Code/deepsource/"
    rules_directory = "./cfn-lint/src/cfnlint/rules"
    directory = os.path.join(base_directory, rules_directory)
    attributes_list = extract_attributes_from_directory(directory)
    for attributes in attributes_list:
        write_to_file(attributes)
