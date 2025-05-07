import pytest
from unittest.mock import patch, MagicMock

from skaf.template_classes.dict_template import DictTemplate
from skaf.template_classes.base import TemplateProperties


class TestDictTemplate:
    
    def test_dict_template_init(self):
        # Setup test data
        template_name = "test_template"
        properties = {"name": "Test Template", "description": "A test template"}
        templates = {
            "file1.py": "content1",
            "file2.py": "content2"
        }
        
        # Create instance
        template = DictTemplate(template_name, properties, templates)
        
        # Verify attributes
        assert template.template_name == template_name
        assert template.properties == properties
        assert hasattr(template, "templates")
        assert template.templates == templates
    
    def test_dict_template_documents(self):
        # Setup test data
        templates = {
            "file1.py": "content1",
            "file2.py": "content2",
            "file3.py": "content3"
        }
        
        # Create instance
        template = DictTemplate("test", {}, templates)
        
        # Get documents
        documents = list(template.documents())
        
        # Verify results
        assert len(documents) == 3
        assert ("file1.py", "content1") in documents
        assert ("file2.py", "content2") in documents
        assert ("file3.py", "content3") in documents
