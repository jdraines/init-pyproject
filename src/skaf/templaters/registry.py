from .base import ABCTemplater
from .pystring import PystringTemplater
from .jinja import Jinja2Templater


_templaters: dict[str, ABCTemplater] = {
    "pystring": PystringTemplater,
    "jinja2": Jinja2Templater,
}


def get_templater(template_name: str, **kwargs) -> ABCTemplater:
    """
    Returns the templater instance for the given template name.
    If the template does not exist, raises a KeyError.
    """
    try:
        return _templaters[template_name](**kwargs)
    except KeyError:
        raise KeyError(f"Templater '{template_name}' does not exist.")
    except Exception as e:
        etype = type(e).__name__
        raise RuntimeError(f"Error getting templater: {etype}: {e}")
