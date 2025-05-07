import pytest
from unittest.mock import patch, MagicMock

from skaf.templaters.base import ABCTemplater


class TestBaseTemplater:
    
    def test_abc_templater_cannot_be_instantiated(self):
        # Verify that ABCTemplater cannot be instantiated directly
        with pytest.raises(TypeError):
            ABCTemplater()
    
    def test_abc_templater_requires_render_method(self):
        # Create a subclass that doesn't implement render
        class IncompleteTemplater(ABCTemplater):
            pass
        
        # Verify that instantiating the subclass raises TypeError
        with pytest.raises(TypeError):
            IncompleteTemplater()
    
    def test_abc_templater_with_render_implementation(self):
        # Create a concrete implementation
        class ConcreteTemplater(ABCTemplater):
            def render(self, template, context):
                return f"Rendered: {template} with {context}"
        
        # Instantiate and verify it works
        templater = ConcreteTemplater()
        result = templater.render("test template", {"var": "value"})
        
        assert result == "Rendered: test template with {'var': 'value'}"
