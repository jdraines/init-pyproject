from abc import ABC, abstractmethod


class ABCTemplater(ABC):
    """
    Abstract base class for all templaters.

    All templaters should inherit from this class and implement the `render` method.
    """

    suffix: str

    @abstractmethod
    def render(self, template: str, context: dict, template_filename: str = None) -> str:
        """
        Render a template with the given context.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        pass

