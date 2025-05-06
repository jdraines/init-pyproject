from abc import ABC, abstractmethod


class ABCTemplater(ABC):
    """
    Abstract base class for all templaters.

    All templaters should inherit from this class and implement the `render` method.
    """

    @abstractmethod
    def render(template: str, context: dict) -> str:
        """
        Render a template with the given context.

        Args:
            template (str): The template to render.
            context (dict): The context to use for rendering.

        Returns:
            str: The rendered template.
        """
        pass

