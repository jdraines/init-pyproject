from dataclasses import dataclass
from pathlib import Path
import os

from ..template_classes.base import BaseTemplate
from ..registry import get_template
from ..templaters.base import ABCTemplater
from ..templaters.registry import get_templater
from .utils import sanitize_project_name


DEFAULT_TEMPLATER = os.environ.get('SKAF_TEMPLATER', 'jinja2')


@dataclass
class ScaffoldContext:
    project_name: str
    template_name: str
    output_dir: Path
    overwrite: bool = False
    auto_use_defaults: bool | None = None
    project_path: Path = None
    template: BaseTemplate = None
    templater: ABCTemplater = None
    variables_filepath: Path | None = None
    _debug: bool = False

    def __post_init__(self):
        self.project_name = sanitize_project_name(self.project_name)
        self.project_path = self.output_dir / self.project_name
        if not self.template and self.template_name:
            self.template = get_template(self.template_name)
        elif not self.template:
            raise ValueError("Either template or template_name must be provided.")
        self.templater = get_templater(self.template.properties.get('templater', DEFAULT_TEMPLATER))
        if self.auto_use_defaults is None:
            self.auto_use_defaults = self.template.properties.get('auto_use_defaults', False)
