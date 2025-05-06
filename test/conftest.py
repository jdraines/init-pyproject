import os
import tempfile
import shutil
from pathlib import Path
import pytest
from typing import Generator

from perigramma.template_classes.filesystem_template import FilesystemTemplate
from perigramma.templaters.jinja import Jinja2Templater
from perigramma.templaters.pystring import PystringTemplater


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    try:
        yield Path(temp_path)
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_template_dir(temp_dir) -> Path:
    """Create a sample template directory structure for testing."""
    # Create template directory
    template_dir = temp_dir / "test_template"
    template_content_dir = template_dir / "template"
    template_content_dir.mkdir(parents=True)

    # Create template properties file
    props_content = {
        "templater": "jinja2",
        "custom_variables": [
            {
                "name": "author",
                "type": "str",
                "default": "Test Author",
                "description": "The author of the project"
            },
            {
                "name": "version",
                "type": "str",
                "default": "0.1.0"
            }
        ]
    }
    
    import yaml
    with open(template_dir / "template_properties.yaml", "w") as f:
        yaml.dump(props_content, f)

    # Create template files
    with open(template_content_dir / "pyproject.toml.template", "w") as f:
        f.write("""[project]
name = "{{ project_name }}"
version = "{{ version }}"
authors = [{ name = "{{ author }}" }]
""")

    with open(template_content_dir / "README.md.template", "w") as f:
        f.write("""# {{ project_name }}

A project by {{ author }}.
""")

    # Create a template with path variables
    src_dir = template_content_dir / "src" / "{{ project_name }}"
    src_dir.mkdir(parents=True)
    
    with open(src_dir / "__init__.py", "w") as f:
        f.write("""# {{ project_name }} package
""")

    with open(src_dir / "main.py", "w") as f:
        f.write("""def main():
    print("Welcome to {{ project_name }}!")

if __name__ == "__main__":
    main()
""")

    return template_dir


@pytest.fixture
def sample_pystring_template_dir(temp_dir) -> Path:
    """Create a sample template directory with pystring templating."""
    # Create template directory
    template_dir = temp_dir / "test_pystring_template"
    template_content_dir = template_dir / "template"
    template_content_dir.mkdir(parents=True)

    # Create template properties file
    props_content = {
        "templater": "pystring",
        "custom_variables": [
            {
                "name": "author",
                "type": "str",
                "default": "Test Author"
            }
        ]
    }
    
    import yaml
    with open(template_dir / "template_properties.yaml", "w") as f:
        yaml.dump(props_content, f)

    # Create template files
    with open(template_content_dir / "pyproject.toml.template", "w") as f:
        f.write("""[project]
name = "${project_name}"
version = "0.1.0"
authors = [{ name = "${author}" }]
""")

    # Create a template with path variables
    src_dir = template_content_dir / "src" / "${project_name}"
    src_dir.mkdir(parents=True)
    
    with open(src_dir / "__init__.py", "w") as f:
        f.write("""# ${project_name} package
""")

    return template_dir


@pytest.fixture
def filesystem_template(sample_template_dir) -> FilesystemTemplate:
    """Create a FilesystemTemplate instance for testing."""
    return FilesystemTemplate("test_template", str(sample_template_dir))


@pytest.fixture
def pystring_filesystem_template(sample_pystring_template_dir) -> FilesystemTemplate:
    """Create a FilesystemTemplate with pystring templating for testing."""
    return FilesystemTemplate("test_pystring_template", str(sample_pystring_template_dir))


@pytest.fixture
def jinja2_templater() -> Jinja2Templater:
    """Create a Jinja2Templater instance for testing."""
    return Jinja2Templater()


@pytest.fixture
def pystring_templater() -> PystringTemplater:
    """Create a PystringTemplater instance for testing."""
    return PystringTemplater()