import pytest
from unittest.mock import patch, MagicMock

from skaf.registry import (
    register_template,
    get_template,
    load_and_register_packaged_templates,
    RegisterTemplateError,
    LoadTemplateError
)
from skaf.template_classes.base import BaseTemplate


class MockTemplate(BaseTemplate):
    def __init__(self, template_name, properties=None):
        self._init(template_name, properties or {})
    
    def documents(self):
        yield "test.txt", "test content"


class TestTemplateRegistry:
    def test_register_and_get_template(self):
        # Register a template
        template = MockTemplate("test_mock_template")
        register_template(template)
        
        # Get the template
        retrieved = get_template("test_mock_template")
        assert retrieved == template
    
    def test_register_duplicate_template(self):
        # Register a template
        template1 = MockTemplate("duplicate_template")
        register_template(template1)
        
        # Try to register another with the same name
        template2 = MockTemplate("duplicate_template")
        with pytest.raises(RegisterTemplateError):
            register_template(template2)
    
    def test_register_invalid_template(self):
        # Try to register something that's not a BaseTemplate
        with pytest.raises(RegisterTemplateError):
            register_template("not a template")
    
    def test_get_nonexistent_template(self):
        # Try to get a template that doesn't exist
        with pytest.raises(LoadTemplateError):
            get_template("nonexistent_template")
    
    def test_none_template_not_registered(self):
        # The "none" template should not be registered
        none_template = MockTemplate("none")
        register_template(none_template)
        
        # Trying to get it should fail
        with pytest.raises(LoadTemplateError):
            get_template("none")


@patch('skaf.registry.FilesystemTemplate')
@patch('skaf.registry.template_lib_dir')
class TestLoadTemplates:
    def test_load_and_register_packaged_templates(self, mock_template_lib_dir, mock_filesystem_template):
        # Setup mock
        mock_dir1 = MagicMock()
        mock_dir1.name = "template1"
        mock_dir1.is_dir.return_value = True
        
        mock_dir2 = MagicMock()
        mock_dir2.name = "template2"
        mock_dir2.is_dir.return_value = True
        
        mock_file = MagicMock()
        mock_file.is_dir.return_value = False
        
        mock_template_lib_dir.iterdir.return_value = [mock_dir1, mock_dir2, mock_file]
        
        # Create mock templates
        mock_template1 = MockTemplate("template1")
        mock_template2 = MockTemplate("template2")
        
        mock_filesystem_template.side_effect = [mock_template1, mock_template2]
        
        # Run the function
        load_and_register_packaged_templates()
        
        # Check that the templates were created and registered
        assert mock_filesystem_template.call_count == 2
        
        # Should be able to get the templates
        assert get_template("template1") == mock_template1
        assert get_template("template2") == mock_template2
    
    def test_load_templates_with_error(self, mock_template_lib_dir, mock_filesystem_template):
        # Setup mock to raise an exception
        mock_dir = MagicMock()
        mock_dir.name = "error_template"
        mock_dir.is_dir.return_value = True
        
        mock_template_lib_dir.iterdir.return_value = [mock_dir]
        
        mock_filesystem_template.side_effect = Exception("Test error")
        
        # Run the function - should raise LoadTemplateError
        with pytest.raises(LoadTemplateError):
            load_and_register_packaged_templates()
