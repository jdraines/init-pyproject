from typing import Callable

from .base import BaseTemplate, TemplateProperties


class DictTemplate(BaseTemplate):

    def __init__(self,
                 template_name: str,
                 properties: TemplateProperties,
                 templates: dict[str, str],
                 variables_helper: Callable[[dict], dict] = None,
                 ):
        self._init(template_name, properties)
        self.templates = templates
        self.variables_helper = variables_helper or (lambda d: d)

    def documents(self):
        """
        Yields tuples of (relpath, content) for each document in the template.
        """
        for filename, content in self.templates.items():
            yield filename, content
