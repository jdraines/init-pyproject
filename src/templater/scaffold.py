# init_pyproject/scaffold.py
import os
import re
import sys
from pathlib import Path
import yaml
from typing import Any

from string import Template
from .template_classes.base import TemplateProperties, BaseTemplate
from .registry import get_template

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


def apply_templating(document: str, variables: dict[str, Any]) -> str:
    """
    Applies templating to the given document string using the provided variables.
    The document can contain placeholders in the form of ${variable_name}.
    """
    template = Template(document)
    try:
        return template.safe_substitute(variables)
    except KeyError as e:
        raise ValueError(f"Missing variable for templating: {e}")
    except Exception as e:
        raise RuntimeError(f"Error applying templating: {e}")


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


def get_template_variable_values(project_name, template_properties) -> dict[str, Any]:
    values = {}
    for custom_var in template_properties.get('custom_variables', []):
        varname = custom_var['name']
        vartype = custom_var.get('type', 'str')
        caster = custom_var_type_mapper.get(vartype, str)
        if (val := custom_var.get('default')) is not None:
            try:
                values[varname] = caster(val)
            except ValueError as e:
                print(f"Default value for {varname}, {val} cannot be used with caster {caster}: {e}")
                sys.exit(1)
        else:
            val = input(f"Enter value for {varname} ({vartype}): ")
            try:
                values[varname] = caster(val)
            except ValueError as e:
                print(f"Invalid value for {varname} with type {vartype} and caster {caster}: {e}")
                sys.exit(1)
    values.update({"project_name": project_name})
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


def map_paths(template: BaseTemplate, project_dir: Path, variables: dict[str, Any]) -> dict[Path, str]:
    """
    Using the `template.documents` iterator method, get the `relpath, content` pairs
    and create a new `target_path, content` mapping. Perform templating on the template
    relpath using the provided variables.
    """
    targets = {}
    for relpath, content in template.documents():
        relpath = Path(apply_templating(relpath, variables))
        target_path = project_dir / relpath
        target_path.parent.mkdir(parents=True, exist_ok=True)
        targets[relpath] = content
    return targets


def scaffold_project(project_name: str,
                     template_name: str = None,
                     output_dir: str = None,
                     force: bool = False,
                     template: BaseTemplate = None,
                     ) -> None:
    """
    Scaffold a new project based on the provided template and variables.
    Copies files from the template directory to the new project directory,
    replacing placeholders with the provided variable values.
    """    
    if output_dir is None:
        output_dir = os.getcwd()
    output_dir = Path(output_dir)
    project_path: Path = output_dir / project_name
    project_name = sanitize_project_name(project_name)
    
    if not template and template_name:
        template = get_template(template_name)
    else:
        raise ValueError("Either template or template_name must be provided.")

    template_properties = template.properties
    variables = get_template_variable_values(project_name, template_properties)
    path_mapping: dict[Path, str] = map_paths(template, project_path)

    if not force:
        if project_path.exists() and project_path.is_dir() and os.listdir(project_path):
            print(f"Project directory '{project_path}' already exists. Set --force to overwrite.")
            sys.exit(1)

    project_path.mkdir(parents=True, exist_ok=True)

    for target_path, content in path_mapping.items():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = apply_templating(content, variables)
        with open(target_path, 'w') as file:
            file.write(content)
