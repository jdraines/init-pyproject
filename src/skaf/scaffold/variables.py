from typing import Any
from .context import ScaffoldContext
import re
import sys
import os

ENV_VAR_PREFIX = "SKAF_"


custom_var_type_mapper = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'list': lambda x: [x.strip() for x in x.split(',')],
    'dict': lambda x: dict(item.split('=') for item in x.split(',')),
}


def add_project_name_variables(project_name: str, variables):
    """
    Adds project name and several other derivatives (project_name_snake, project_name_pascal, project_name_kebab)"""
    variables['project_name'] = project_name
    project_name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', project_name).lower().replace("-", "_")
    variables['project_name_snake'] = project_name_snake
    variables['project_name_pascal'] = ''.join(word.capitalize() for word in project_name_snake.split('_'))
    variables['project_name_kebab'] = project_name_snake.replace('_', '-')
    variables['project_name_title'] = project_name.replace("_", " ").title()
    return variables


def get_env_variable(name: str) -> Any:
    """
    Get the value of an environment variable, or None if not set.
    """
    env_var = ENV_VAR_PREFIX + str(name)
    return os.environ.get(env_var)


def get_variable_values(context: ScaffoldContext) -> dict[str, Any]:
    values = {}
    for custom_var in context.template.custom_variables:
        varname = custom_var['name']
        vartype = custom_var.get('type', 'str')
        caster = custom_var_type_mapper.get(vartype, str)
        default = custom_var.get('default')
        if (from_env := get_env_variable(varname)) is not None:
            try:
                values[varname] = caster(from_env)
                continue
            except Exception as e:
                raise type(e)(f"Environment variable {from_env} cannot be used with caster {caster}: {e}")
        if context.auto_use_defaults and default is not None:
            try:
                values[varname] = caster(default)
            except Exception as e:
                raise type(e)(f"Default value for {varname}, {default} cannot be used with caster {caster}: {e}")
        else:
            defaultstr = f" [{default}]" if default else ""
            val = input(f"Enter value for {varname} ({vartype}){defaultstr}: ")
            if not val and default is not None:
                val = default
            try:
                values[varname] = caster(val)
            except Exception as e:
                raise type(e)(f"Invalid value for {varname} with type {vartype} and caster {caster}: {e}")
                
    values = add_project_name_variables(context.project_name, values)
    return values
