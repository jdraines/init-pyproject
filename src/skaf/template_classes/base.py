from abc import ABC, abstractmethod
from typing import Generator, Callable

from ..properties import TemplateProperties


class ABCTemplate(ABC):

    template_name: str
    properties: TemplateProperties
    variables_helper: Callable[[dict], dict]

    @abstractmethod
    def documents(self) -> Generator[tuple[str, str], None, None]:
        """
        Yields tuples of (relpath, content) for each document in the template.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class BaseTemplate(ABCTemplate):

    def _init(self,
              template_name: str,
              properties: TemplateProperties,
              ) -> None:
        """
        Initializes the template with the given name and properties.
        """
        self.template_name = template_name
        self.properties = properties or {}
        self.variables_helper = lambda d: d

    @property
    def custom_variables(self) -> list[str]:
        """
        Returns a list of custom variable names defined in the template properties.
        """
        return self.properties.get('custom_variables', [])
