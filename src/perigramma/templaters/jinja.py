import jinja2

from .base import ABCTemplater


class Jinja2Templater(ABCTemplater):

    environment_parameters = {
        "undefined": jinja2.StrictUndefined,
    }
    
    def render(self, template: str, context: dict) -> str:
        """
        Render a template with the given context using Jinja2 templating.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        environment = jinja2.Environment(**self.environment_parameters)
        template: jinja2.environment.Template = environment.from_string(template)
        return template.render(**context)
