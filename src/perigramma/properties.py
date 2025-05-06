from typing import Any, TypedDict, Literal


class CustomVariable(TypedDict):
    name: str
    type: str | None
    default: Any | None
    description: str | None


class TemplateProperties(TypedDict):
    custom_variables: list[CustomVariable] | None
    templater: Literal["pystring", "jinja2"] | None
    auto_use_defaults: bool | None
