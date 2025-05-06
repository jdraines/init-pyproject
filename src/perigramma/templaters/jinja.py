import jinja2

from .base import ABCTemplater


class Jinja2Templater(ABCTemplater):

    environment_parameters = {
        "undefined": jinja2.StrictUndefined
    }
    
    suffix = ".jinja"

    def render(self, template: str, context: dict, template_filename: str = None) -> str:
        """
        Render a template with the given context using Jinja2 templating.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        if template_filename:
            if not template_filename.endswith(self.suffix):
                return template
        environment = jinja2.Environment(**self.environment_parameters)
        template: jinja2.environment.Template = environment.from_string(template)
        return template.render(**context)
