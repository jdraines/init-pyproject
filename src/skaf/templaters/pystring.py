from string import Template

from .base import ABCTemplater


class PystringTemplater(ABCTemplater):

    suffix = ".template"

    def render(self, template: str, context: dict, template_filename: str = None) -> str:
        """
        Render a template with the given context using Python string templating.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        if template_filename:
            if not template_filename.endswith(self.suffix):
                return template
        pystring_template = Template(template)
        return pystring_template.safe_substitute(context)
