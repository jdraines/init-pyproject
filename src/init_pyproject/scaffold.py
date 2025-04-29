# init_pyproject/scaffold.py
import os
import re
import sys
from pathlib import Path
import yaml
from typing import Any

template_lib_dir = Path(__file__).parent / 'template_lib'
TEMPLATE_PROPERTIES_FILENAME = 'template_properties.yaml'

custom_var_type_mapper = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'list': lambda x: [x.strip() for x in x.split(',')],
    'dict': lambda x: dict(item.split('=') for item in x.split(',')),
}


def get_template_dir(template_name: str) -> Path:
    """
    Returns the path to the specified template directory.
    If the template does not exist, raises a FileNotFoundError.
    """
    template_path = template_lib_dir / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{template_name}' does not exist.")
    return template_path


def load_template_properties(template_name) -> dict:
    template_dir = get_template_dir(template_name)
    properties_filename = template_dir / TEMPLATE_PROPERTIES_FILENAME
    with open(properties_filename, 'r') as file:
        properties = yaml.safe_load(file)
    return properties


def get_template_variable_values(template_properties) -> dict[str, Any]:
    values = {}
    for custom_var in template_properties.get('custom_variables', []):
        varname = custom_var['name']
        vartype = custom_var.get('type', 'str')
        caster = custom_var_type_mapper.get(vartype, str)
        val = input(f"Enter value for {varname} ({vartype}): ")
        try:
            values[varname] = caster(val)
        except ValueError as e:
            print(f"Invalid value for {varname}: {e}")
            sys.exit(1)
    return values


def sanitize_project_name(name: str) -> str:
    """
    Converts the provided project name to a valid Python package name.
    Lowercases the name, replaces non-alphanumeric characters with underscores,
    and prepends an underscore if the name starts with a digit.
    """
    name = name.lower()
    sanitized = re.sub(r'\W+', '_', name)
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized


def walkdirs_map_all_paths(template_dir, project_name):
    """
    Walk all the files and dires in the template directory and put the relative
    path in a list of current_dir_paths. Create a dictionary that maps
    the relative current_dir_paths to their absolute template paths.
    """
    template_paths = {}

    template_root = template_dir / "template"

    for root, dirs, files in os.walk(template_dir):
        rel_root = Path(root).relative_to(template_dir)
        for name in dirs + files:
            rel_path_template = rel_root / name
            rel_path_target = Path(str(rel_path_template).format(project_name=project_name))
            template_paths[str(rel_path_target)] = template_dir / rel_path_template

    return template_paths


def scaffold_project(project_name: str, template_name: str):
    """
    Scaffold a new project based on the provided template and variables.
    Copies files from the template directory to the new project directory,
    replacing placeholders with the provided variable values.
    """
    project_name = sanitize_project_name(project_name)
    template_dir = get_template_dir(template_name)
    template_properties = load_template_properties(template_name)
    variables = get_template_variable_values(template_properties)
    path_mapping = walkdirs_map_all_paths(template_dir, project_name)
    project_path = Path(project_name)

    if project_path.exists():
        print(f"Project directory '{project_path}' already exists.")
        sys.exit(1)

    project_path.mkdir(parents=True, exist_ok=True)

    for rel_path, abs_template_path in path_mapping.items():
        target_path = project_path / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if abs_template_path.is_file():
            with open(abs_template_path, 'r') as file:
                content = file.read()
            for varname, value in variables.items():
                content = content.replace(f'{{{{ {varname} }}}}', str(value))
            with open(target_path, 'w') as file:
                file.write(content)
        else:
            target_path.mkdir(parents=True, exist_ok=True)

    print(f"Project '{project_name}' scaffolded successfully at {project_path}.")
