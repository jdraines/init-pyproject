import os
import re
import sys
from pathlib import Path
import yaml
from typing import Any
from dataclasses import dataclass, field

from string import Template
from .template_classes.base import BaseTemplate
from .registry import get_template
from .templaters.base import ABCTemplater
from .templaters.registry import get_templater

template_lib_dir = Path(__file__).parent / 'template_lib'
TEMPLATE_PROPERTIES_FILENAME = 'template_properties.yaml'
DEFAULT_TEMPLATER = os.environ.get('skaf_TEMPLATER', 'jinja2')


@dataclass
class ScaffoldContext:
    project_name: str
    template_name: str
    output_dir: Path
    force: bool = False
    auto_use_defaults: bool | None = None
    project_path: Path = None
    template: BaseTemplate = None
    templater: ABCTemplater = None

    def __post_init__(self):
        self.project_name = sanitize_project_name(self.project_name)
        self.project_path = self.output_dir / self.project_name
        if not self.template and self.template_name:
            self.template = get_template(self.template_name)
        elif not self.template:
            raise ValueError("Either template or template_name must be provided.")
        self.templater = get_templater(self.template.properties.get('templater', DEFAULT_TEMPLATER))
        if self.auto_use_defaults is None:
            self.auto_use_defaults = self.template.properties.get('auto_use_defaults', False)


custom_var_type_mapper = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'list': lambda x: [x.strip() for x in x.split(',')],
    'dict': lambda x: dict(item.split('=') for item in x.split(',')),
}


def apply_templating(document: str,
                     variables: dict[str, Any],
                     templater: ABCTemplater,
                     document_filename: str = None
                     ) -> str:
    """
    Applies templating to the given document string using the provided variables
    using the specified templater.
    """
    try:
        return templater.render(document, variables, template_filename=document_filename)
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


def add_project_name_variables(project_name: str, variables):
    """
    Adds project name and several other derivatives (project_name_snake, project_name_pascal, project_name_kebab)"""
    variables['project_name'] = project_name
    project_name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', project_name).lower()
    variables['project_name_snake'] = project_name_snake
    variables['project_name_pascal'] = ''.join(word.capitalize() for word in project_name_snake.split('_'))
    variables['project_name_kebab'] = project_name.replace('_', '-')
    variables['project_name_title'] = project_name.replace("_", " ").title()
    return variables


def get_template_variable_values(context: ScaffoldContext) -> dict[str, Any]:
    values = {}
    for custom_var in context.template.custom_variables:
        varname = custom_var['name']
        vartype = custom_var.get('type', 'str')
        caster = custom_var_type_mapper.get(vartype, str)
        default = custom_var.get('default')
        if context.auto_use_defaults and default is not None:
            try:
                values[varname] = caster(default)
            except ValueError as e:
                print(f"Default value for {varname}, {default} cannot be used with caster {caster}: {e}")
                sys.exit(1)
        else:
            defaultstr = f" [{default}]" if default else ""
            val = input(f"Enter value for {varname} ({vartype}){defaultstr}: ")
            if not val and default is not None:
                val = default
            try:
                values[varname] = caster(val)
            except ValueError as e:
                print(f"Invalid value for {varname} with type {vartype} and caster {caster}: {e}")
                sys.exit(1)
    values = add_project_name_variables(context.project_name, values)
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


def map_paths(context: ScaffoldContext,
              variables: dict[str, Any]
              ) -> dict[Path, str]:
    """
    Using the `template.documents` iterator method, get the `relpath, content` pairs
    and create a new `target_path, content` mapping. Perform templating on the template
    relpath using the provided variables.
    """
    targets = {}
    for relpath, content in context.template.documents():
        relpath = Path(apply_templating(relpath, variables, context.templater))
        target_path = context.project_path / relpath
        target_path.parent.mkdir(parents=True, exist_ok=True)
        targets[relpath] = content
    return targets


def scaffold_project(project_name: str,
                     template_name: str = None,
                     output_dir: str = None,
                     force: bool = False,
                     template: BaseTemplate = None,
                     auto_use_defaults: bool = True,
                     ) -> None:
    """
    Scaffold a new project based on the provided template and variables.
    Copies files from the template directory to the new project directory,
    replacing placeholders with the provided variable values.
    """
    if output_dir is None:
        output_dir = os.getcwd()
    output_dir = Path(output_dir)

    context = ScaffoldContext(
        project_name=project_name,
        template_name=template_name,
        output_dir=output_dir,
        force=force,
        auto_use_defaults=auto_use_defaults,
        template=template
    )

    variables = get_template_variable_values(context)

    path_mapping: dict[Path, str] = map_paths(
        context,
        variables
    )

    if not context.force:
        if all([
            context.project_path.exists(),
            context.project_path.is_dir(),
            os.listdir(context.project_path)
        ]):
            print(f"Project directory '{context.project_path}' already exists. Set --force to overwrite.")
            sys.exit(1)

    context.project_path.mkdir(parents=True, exist_ok=True)

    for target_path, content in path_mapping.items():
        target_filename = target_path.name
        content = apply_templating(
            content,
            variables,
            context.templater,
            target_filename
        )
        if target_path.suffix == context.templater.suffix:
            target_path = Path(target_path.stem)
        write_path = context.project_path / target_path
        write_path.parent.mkdir(parents=True, exist_ok=True)
        with open(write_path, 'w') as file:
            file.write(content)
