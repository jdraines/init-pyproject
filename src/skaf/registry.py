from importlib.metadata import entry_points
from pathlib import Path

from .template_classes.base import BaseTemplate
from .template_classes.filesystem_template import FilesystemTemplate


_entry_points_group = "skaf.template"
template_lib_dir = Path(__file__).parent / 'template_lib'


class LoadTemplateError(Exception):
    """
    Exception raised when a template cannot be loaded.
    """
    pass


class RegisterTemplateError(Exception):
    """
    Exception raised when a template cannot be registered.
    """
    pass


_templates = {}


def load_and_register_template_plugins():
    template_entry_points = entry_points(group=_entry_points_group)
    for tep in template_entry_points:
        _template = tep.load()
        register_template(_template)


def load_and_register_packaged_templates():
    """
    Loads and registers all packaged templates.
    """
    for template_dir in template_lib_dir.iterdir():
        if template_dir.is_dir():
            template_name = template_dir.name
            try:
                template = FilesystemTemplate(template_name, template_dir)
                register_template(template)
            except Exception as e:
                etype = type(e).__name__
                raise LoadTemplateError(f"Error loading '{template_name}': {etype}: {e}")


def register_template(template: BaseTemplate):
    """
    Registers a template class with the registry.
    The template class must inherit from BaseTemplate.
    """

    if not isinstance(template, BaseTemplate):
        raise RegisterTemplateError("Template must be a subclass of BaseTemplate.")
    
    template_name = template.template_name
    if template_name == "none":
        return

    if template_name in _templates:
        raise RegisterTemplateError(f"Template '{template_name}' is already registered.")
    
    _templates[template_name] = template


def get_template(template_name: str) -> BaseTemplate:
    """
    Returns the template class registered with the given name.
    If no template is found, raises a KeyError.
    """
    if template_name not in _templates:
        raise LoadTemplateError(f"Template '{template_name}' not found.")
    
    return _templates[template_name]
