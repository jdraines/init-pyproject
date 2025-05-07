import os
import pytest
from pathlib import Path

from skaf.template_classes.filesystem_template import FilesystemTemplate


class TestFilesystemTemplate:
    def test_template_init(self, sample_template_dir):
        template = FilesystemTemplate("test_template", str(sample_template_dir))
        assert template.template_name == "test_template"
        assert template.template_dir == str(sample_template_dir)
        assert template.properties is not None
        assert template.properties.get("templater") == "jinja2"
        assert len(template.properties.get("custom_variables", [])) == 2
    
    def test_load_properties(self, filesystem_template):
        properties = filesystem_template.properties
        assert properties is not None
        assert properties.get("templater") == "jinja2"
        assert len(properties.get("custom_variables", [])) == 2
        
        # Check custom variables
        vars = properties.get("custom_variables", [])
        assert vars[0].get("name") == "author"
        assert vars[0].get("default") == "Test Author"
        assert vars[1].get("name") == "version"
        assert vars[1].get("default") == "0.1.0"
    
    def test_missing_properties_file(self, temp_dir):
        # Create a template dir without a properties file
        bad_template_dir = temp_dir / "bad_template"
        bad_template_dir.mkdir()
        (bad_template_dir / "template").mkdir()
        
        with pytest.raises(FileNotFoundError):
            FilesystemTemplate("bad_template", str(bad_template_dir))
    
    def test_documents_iterator(self, filesystem_template):
        documents = list(filesystem_template.documents())
        assert len(documents) == 4  # We have 4 files in our fixture
        
        # Check that all expected files are included
        paths = [rel_path for rel_path, _ in documents]
        assert "pyproject.toml.jinja" in paths
        assert "README.md.jinja" in paths
        assert "src/{{ project_name }}/__init__.py" in paths
        assert "src/{{ project_name }}/main.py" in paths
        
        # Check content of a specific file
        for rel_path, content in documents:
            if rel_path == "README.md.jinja":
                assert "# {{ project_name }}" in content
                assert "A project by {{ author }}." in content
    
    def test_missing_template_directory(self, temp_dir):
        # Create a template dir without a template subdirectory
        bad_template_dir = temp_dir / "bad_template_dir"
        bad_template_dir.mkdir()
        
        # Add a properties file
        with open(bad_template_dir / "template_properties.yaml", "w") as f:
            f.write("templater: jinja2\n")
        
        template = FilesystemTemplate("bad_template", str(bad_template_dir))
        
        # Should raise when trying to iterate over documents
        with pytest.raises(FileNotFoundError):
            list(template.documents())
    
    def test_custom_variables_property(self, filesystem_template):
        custom_vars = filesystem_template.custom_variables
        assert len(custom_vars) == 2
        assert custom_vars[0]["name"] == "author"
        assert custom_vars[1]["name"] == "version"
