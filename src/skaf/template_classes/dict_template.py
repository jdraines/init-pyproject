from .base import BaseTemplate, TemplateProperties


class DictTemplate(BaseTemplate):

    def __init__(self,
                 template_name: str,
                 properties: TemplateProperties,
                 templates: dict[str, str],
                 ):
        self._init(template_name, properties)
        self.templates = templates

    def documents(self):
        """
        Yields tuples of (relpath, content) for each document in the template.
        """
        for filename, content in self.templates.items():
            yield filename, content
