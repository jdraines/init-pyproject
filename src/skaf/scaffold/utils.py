import re


def sanitize_project_name(name: str) -> str:
    """
    Converts the provided project name to a valid Python package name.
    Lowercases the name, replaces non-alphanumeric characters with underscores,
    and prepends an underscore if the name starts with a digit.
    """
    name = name.lower()
    sanitized = re.sub(r'\W+', '_', name)
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized
