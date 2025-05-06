from string import Template

from .base import ABCTemplater


class PystringTemplater(ABCTemplater):

    def render(self, template: str, context: dict) -> str:
        """
        Render a template with the given context using Python string templating.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        pystring_template = Template(template)
        return pystring_template.safe_substitute(context)
