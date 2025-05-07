import pytest
from unittest.mock import patch, MagicMock

from skaf.templaters.registry import get_templater, _templaters
from skaf.templaters.jinja import Jinja2Templater
from skaf.templaters.pystring import PystringTemplater


class TestTemplaterRegistryAdditional:
    
    def test_templater_registry_contents(self):
        # Verify templater registry contents
        assert 'jinja2' in _templaters
        assert 'pystring' in _templaters
        assert _templaters['jinja2'] == Jinja2Templater
        assert _templaters['pystring'] == PystringTemplater
    
    def test_get_templater_nonexistent_with_exception(self):
        # Call with nonexistent templater - should raise KeyError
        with pytest.raises(KeyError) as excinfo:
            get_templater('nonexistent_templater')
        
        assert "Templater 'nonexistent_templater' does not exist" in str(excinfo.value)
    
    @patch('skaf.templaters.registry._templaters')
    def test_get_templater_with_instantiation_error(self, mock_templaters):
        # Setup mock to raise exception during instantiation
        mock_templater_class = MagicMock(side_effect=ValueError('Templater initialization error'))
        mock_templaters.__getitem__.return_value = mock_templater_class
        
        # Call function and check for RuntimeError
        with pytest.raises(RuntimeError) as excinfo:
            get_templater('error_templater')
        
        assert "Error getting templater: ValueError: Templater initialization error" in str(excinfo.value)
