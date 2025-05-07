import pytest

from skaf.templaters.jinja import Jinja2Templater
from skaf.templaters.pystring import PystringTemplater
from skaf.templaters.registry import get_templater


class TestTemplaters:
    def test_jinja2_templater_rendering(self, jinja2_templater):
        template = "Hello, {{ name }}!"
        context = {"name": "World"}
        result = jinja2_templater.render(template, context)
        assert result == "Hello, World!"

    def test_jinja2_templater_with_loop(self, jinja2_templater):
        template = "{% for i in range(3) %}{{ i }}{% endfor %}"
        result = jinja2_templater.render(template, {})
        assert result == "012"
    
    def test_jinja2_templater_with_condition(self, jinja2_templater):
        template = "{% if value %}Yes{% else %}No{% endif %}"
        assert jinja2_templater.render(template, {"value": True}) == "Yes"
        assert jinja2_templater.render(template, {"value": False}) == "No"
    
    def test_pystring_templater_rendering(self, pystring_templater):
        template = "Hello, ${name}!"
        context = {"name": "World"}
        result = pystring_templater.render(template, context)
        assert result == "Hello, World!"
    
    def test_pystring_templater_missing_var(self, pystring_templater):
        template = "Hello, ${name}!"
        context = {}
        # PystringTemplater uses safe_substitute which doesn't raise an error
        result = pystring_templater.render(template, context)
        assert result == "Hello, ${name}!"


class TestTemplaterRegistry:
    def test_get_jinja2_templater(self):
        templater = get_templater("jinja2")
        assert isinstance(templater, Jinja2Templater)
    
    def test_get_pystring_templater(self):
        templater = get_templater("pystring")
        assert isinstance(templater, PystringTemplater)
    
    def test_get_nonexistent_templater(self):
        with pytest.raises(KeyError):
            get_templater("nonexistent")
