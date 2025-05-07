import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from copy import copy

from skaf.scaffold.scaffold import (
    apply_templating,
    map_paths,
    scaffold_project,
    get_template_variable_values,
    get_package_template_dir,
    load_template_properties
)

from skaf.scaffold.context import (
    ScaffoldContext,
)

from skaf.scaffold.variables import (
    get_variable_values,
    add_project_name_variables
)

from skaf.scaffold.utils import (
    sanitize_project_name
)

from skaf.templaters.jinja import Jinja2Templater
from skaf.template_classes.filesystem_template import FilesystemTemplate


class TestScaffoldUtilities:
    def test_sanitize_project_name(self):
        # Test basic lowercase conversion
        assert sanitize_project_name("MyProject") == "myproject"
        
        # Test replacing spaces and special chars with underscores
        assert sanitize_project_name("My Project!") == "my_project_"
        
        # Test handling numbers at the beginning
        assert sanitize_project_name("123project") == "_123project"
        
        # Test complex case
        assert sanitize_project_name("123 My-Project!") == "_123_my_project_"
    
    def test_apply_templating(self):
        templater = Jinja2Templater()
        document = "Hello {{ name }}!"
        variables = {"name": "World"}
        
        result = apply_templating(document, variables, templater)
        assert result == "Hello World!"
        
        # Test missing variable
        with pytest.raises(RuntimeError):
            apply_templating("Hello {{ missing }}!", {}, templater)
    
    def test_add_project_name_variables(self):
        variables = {}
        result = add_project_name_variables("my_project", variables)
        
        assert result["project_name"] == "my_project"
        assert result["project_name_snake"] == "my_project"
        assert result["project_name_pascal"] == "MyProject"
        assert result["project_name_kebab"] == "my-project"
        assert result["project_name_title"] == "My Project"
        
        # Test with camelCase
        variables = {}
        result = add_project_name_variables("myProject", variables)
        
        assert result["project_name"] == "myProject"
        assert result["project_name_snake"] == "my_project"
        assert result["project_name_pascal"] == "MyProject"


class TestGetTemplateVariableValues:
    
    @patch('builtins.input')
    def test_get_template_variable_values_with_user_input(self, mock_input):
        # Setup mock template and context
        mock_template = MagicMock()
        mock_template.custom_variables = [
            {'name': 'author', 'type': 'str'},
            {'name': 'version', 'type': 'str', 'default': '0.1.0'}
        ]
        
        context = MagicMock()
        context.template = mock_template
        context.project_name = 'test_project'
        context.auto_use_defaults = False
        
        # Setup input responses
        mock_input.side_effect = ['John Doe', '']
        
        # Call function
        result = get_template_variable_values(context)
        
        # Verify results
        assert result['author'] == 'John Doe'
        assert result['version'] == '0.1.0'
        assert result['project_name'] == 'test_project'
        assert 'project_name_snake' in result
        assert 'project_name_pascal' in result
    
    def test_get_template_variable_values_with_defaults(self):
        # Setup mock template and context
        mock_template = MagicMock()
        mock_template.custom_variables = [
            {'name': 'author', 'type': 'str', 'default': 'Default Author'},
            {'name': 'version', 'type': 'str', 'default': '0.1.0'},
            {'name': 'keywords', 'type': 'list', 'default': 'one,two,three'}
        ]
        
        context = MagicMock()
        context.template = mock_template
        context.project_name = 'test_project'
        context.auto_use_defaults = True
        
        # Call function
        result = get_template_variable_values(context)
        
        # Verify results
        assert result['author'] == 'Default Author'
        assert result['version'] == '0.1.0'
        assert result['keywords'] == ['one', 'two', 'three']
        assert result['project_name'] == 'test_project'

    @patch('builtins.input')
    @patch('sys.exit')
    def test_get_template_variable_values_with_invalid_input(self, mock_exit, mock_input):
        # Setup mock template and context
        mock_template = MagicMock()
        mock_template.custom_variables = [
            {'name': 'number', 'type': 'int'}
        ]
        
        context = MagicMock()
        context.template = mock_template
        context.project_name = 'test_project'
        context.auto_use_defaults = False
        context._debug = True
        
        # Setup input to cause ValueError
        mock_input.return_value = 'not-a-number'
        
        # Call function
        with pytest.raises(ValueError):
            get_template_variable_values(context)
        


class TestGetTemplateDir:
    
    @patch('pathlib.Path.exists')
    def test_get_package_template_dir_exists(self, mock_exists):
        # Setup mock
        mock_exists.return_value = True
        
        # Call function
        result = get_package_template_dir('test_template')
        
        # Verify result is a Path object ending with test_template
        assert isinstance(result, Path)
        assert result.name == 'test_template'
    
    @patch('pathlib.Path.exists')
    def test_get_template_dir_not_exists(self, mock_exists):
        # Setup mock
        mock_exists.return_value = False
        
        # Call function and verify exception
        with pytest.raises(FileNotFoundError) as excinfo:
            get_package_template_dir('nonexistent_template')
        
        # Verify error message
        assert "Template 'nonexistent_template' does not exist" in str(excinfo.value)


class TestLoadTemplateProperties:
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="name: test\ndescription: Test Template")
    @patch('yaml.safe_load')
    def test_load_template_properties(self, mock_yaml_load, mock_file, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            'name': 'test',
            'description': 'Test Template'
        }
        
        # Call function
        result = load_template_properties('test_template')
        
        # Verify results
        assert result == {'name': 'test', 'description': 'Test Template'}
        mock_yaml_load.assert_called_once()


class TestScaffoldContext:
    def test_scaffold_context_initialization(self, filesystem_template, temp_dir):
        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template
        )
        
        assert context.project_name == "test_project"
        assert context.project_path == temp_dir / "test_project"
        assert context.template == filesystem_template
        assert context.template_name == "test_template"
        assert context.templater is not None
    
    def test_scaffold_context_with_sanitization(self, filesystem_template, temp_dir):
        context = ScaffoldContext(
            project_name="Test Project!",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template
        )
        
        # Should sanitize the project name
        assert context.project_name == "test_project_"
        assert context.project_path == temp_dir / "test_project_"
    
    def test_scaffold_context_without_template(self, temp_dir):
        with pytest.raises(ValueError):
            ScaffoldContext(
                project_name="test_project",
                template_name=None,
                output_dir=temp_dir,
                template=None
            )
    
    def test_scaffold_context_with_auto_use_default_values(self, filesystem_template, temp_dir):
        filesystem_template = copy(filesystem_template)
        filesystem_template.properties = copy(filesystem_template.properties)

        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template,
            auto_use_defaults=True
        )
        assert context.auto_use_defaults is True

        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template,
            auto_use_defaults=False
        )
        assert context.auto_use_defaults is False

        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template,
            auto_use_defaults=None
        ) 
        assert context.auto_use_defaults is True

        filesystem_template.properties["auto_use_defaults"] = False
        assert filesystem_template.properties["auto_use_defaults"] is False
        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template,
            auto_use_defaults=None
        ) 
        assert context.auto_use_defaults is False

        filesystem_template.properties.pop("auto_use_defaults")
        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template,
            auto_use_defaults=None
        ) 
        assert context.auto_use_defaults is False

class TestMapPaths:
    def test_map_paths_basic(self, filesystem_template, temp_dir):
        context = ScaffoldContext(
            project_name="test_project",
            template_name="test_template",
            output_dir=temp_dir,
            template=filesystem_template
        )
        
        variables = {"project_name": "test_project", "author": "Test Author", "version": "0.1.0"}
        path_mapping = map_paths(context, variables)
        
        # Check that the expected files are in the mapping
        paths = list(path_mapping.keys())
        assert Path("pyproject.toml.jinja") in paths
        assert Path("README.md.jinja") in paths
        assert Path("src/test_project/__init__.py") in paths  # project_name substituted
        assert Path("src/test_project/main.py") in paths  # project_name substituted


class TestScaffoldProject:
    @patch('skaf.scaffold.scaffold.get_template_variable_values')
    def test_scaffold_project_basic(self, mock_get_vars, filesystem_template, temp_dir):
        # Setup mock
        mock_get_vars.return_value = {
            "project_name": "test_project", 
            "author": "Test Author", 
            "version": "0.1.0",
            "project_name_snake": "test_project",
            "project_name_pascal": "TestProject",
            "project_name_kebab": "test-project",
            "project_name_title": "Test_project"
        }
        
        # Run the scaffold function
        scaffold_project(
            project_name="test_project",
            template_name="test_template",
            output_dir=str(temp_dir),
            template=filesystem_template,
            auto_use_defaults=True,
            force=True
        )
        
        # Check that the expected files were created
        project_dir = temp_dir / "test_project"
        assert project_dir.exists()
        
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "src" / "test_project" / "__init__.py").exists()
        assert (project_dir / "src" / "test_project" / "main.py").exists()
        
        # Check file content
        with open(project_dir / "README.md") as f:
            content = f.read()
            assert "# test_project" in content
            assert "A project by Test Author" in content
    
    @patch('skaf.scaffold.scaffold.get_template_variable_values')
    def test_scaffold_project_existing_dir(self, mock_get_vars, filesystem_template, temp_dir):
        # Setup mock
        mock_get_vars.return_value = {
            "project_name": "test_project", 
            "author": "Test Author",
            "version": "0.1.0",
            "project_name_snake": "test_project",
            "project_name_pascal": "TestProject",
            "project_name_kebab": "test-project",
            "project_name_title": "Test_project"
        }
        
        # Create the project dir and a file in it
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "existing_file.txt").touch()
        
        # Without force, should raise SystemExit
        with pytest.raises(SystemExit):
            scaffold_project(
                project_name="test_project",
                template_name="test_template",
                output_dir=str(temp_dir),
                template=filesystem_template,
                force=False,
                auto_use_defaults=True
            )
        
        # With force, should work
        scaffold_project(
            project_name="test_project",
            template_name="test_template",
            output_dir=str(temp_dir),
            template=filesystem_template,
            force=True,
            auto_use_defaults=True
        )
        
        # Check that the expected files were created
        assert (project_dir / "pyproject.toml").exists()
        assert (project_dir / "existing_file.txt").exists()  # Original file should still be there
    
    @patch('skaf.scaffold.scaffold.ScaffoldContext')
    @patch('skaf.scaffold.scaffold.get_template_variable_values')
    @patch('skaf.scaffold.scaffold.map_paths')
    @patch('os.listdir')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('skaf.scaffold.scaffold.apply_templating')
    def test_scaffold_project_mock_implementation(self, mock_apply_templating, mock_open_file, mock_mkdir,
                                     mock_exists, mock_listdir, mock_map_paths, mock_get_vars, mock_context, filesystem_template):
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context_instance.template_name = 'test_template'
        mock_context_instance.project_name = 'test_project'
        mock_context_instance.project_path = Path('/output/test_project')
        mock_context_instance.force = False
        mock_context.return_value = mock_context_instance
        mock_context._debug = False
        
        mock_get_vars.return_value = {'project_name': 'test_project'}
        
        mock_map_paths.return_value = {
            Path('file1.py'): 'content1',
            Path('file2.py'): 'content2'
        }
        
        # Setup directory checks
        mock_exists.return_value = False
        mock_listdir.return_value = []
        
        mock_apply_templating.side_effect = lambda c, v, t, f: c + '_templated'
        
        # Call function
        scaffold_project(
            project_name='test_project',
            template_name='test_template',
            template=filesystem_template,
            output_dir='/output',
            force=False
        )
        
        # Verify results
        mock_context.assert_called_once()
        mock_get_vars.assert_called_once_with(mock_context_instance)
        mock_map_paths.assert_called_once_with(mock_context_instance, {'project_name': 'test_project'})
        assert mock_open_file.call_count == 2
        assert mock_apply_templating.call_count == 2
    
    @patch('skaf.scaffold.scaffold.ScaffoldContext')
    @patch('os.listdir')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.mkdir')
    @patch('sys.exit')
    def test_scaffold_project_existing_dir_no_force_mock(self, mock_exit, mock_mkdir, mock_is_dir,
                                                 mock_exists, mock_listdir, mock_context, filesystem_template):
        # Setup mocks
        mock_context_instance = MagicMock()
        mock_context_instance.template_name = 'test_template'
        mock_context_instance.project_name = 'test_project'
        mock_context_instance.project_path = Path('/output/test_project')
        mock_context_instance.force = False
        mock_context.return_value = mock_context_instance
        
        # Setup directory checks to indicate it exists with files
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_listdir.return_value = ['existing_file.py']
        
        # Call function
        with patch('builtins.print') as mock_print:
            scaffold_project(
                project_name='test_project',
                template_name='test_template',
                output_dir='/output',
                force=False,
                template=filesystem_template
            )
        
        # Verify exit due to existing directory
        mock_print.assert_called_once_with(
            "Project directory '/output/test_project' already exists. Set --force to overwrite."
        )
        mock_exit.assert_called_once_with(1)
