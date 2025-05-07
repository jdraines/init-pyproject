import os
import sys
from pathlib import Path
import yaml
from typing import Any

from ..template_classes.base import BaseTemplate
from ..templaters.base import ABCTemplater
from .variables import get_variable_values
from .context import ScaffoldContext


template_lib_dir = Path(__file__).parent / 'template_lib'
TEMPLATE_PROPERTIES_FILENAME = 'template_properties.yaml'


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


def get_package_template_dir(template_name: str) -> Path:
    """
    Returns the path to the specified template directory.
    If the template does not exist, raises a FileNotFoundError.
    """
    template_path = template_lib_dir / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{template_name}' does not exist.")
    return template_path


def load_template_properties(template_name) -> dict:
    template_dir = get_package_template_dir(template_name)
    properties_filename = template_dir / TEMPLATE_PROPERTIES_FILENAME
    with open(properties_filename, 'r') as file:
        properties = yaml.safe_load(file)
    return properties


def get_template_variable_values(context: ScaffoldContext) -> dict[str, Any]:
    try:
        return get_variable_values(context)
    except Exception as e:
        if context._debug:
            raise
        etype = type(e).__name__
        print(f"Error getting variable values: {etype}: {e}")
        sys.exit(1)


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
                     overwrite: bool = False,
                     template: BaseTemplate = None,
                     auto_use_defaults: bool = True,
                     varfile: str | None = None,
                     _debug: bool = False
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
        overwrite=overwrite,
        auto_use_defaults=auto_use_defaults,
        template=template,
        variables_filepath=Path(varfile) if varfile else None,
        _debug=_debug
    )

    variables = get_template_variable_values(context)

    path_mapping: dict[Path, str] = map_paths(
        context,
        variables
    )

    if not context.overwrite:
        if all([
            context.project_path.exists(),
            context.project_path.is_dir(),
            os.listdir(context.project_path)
        ]):
            print(f"Project directory '{context.project_path}' already exists. Set --overwrite to overwrite.")
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
