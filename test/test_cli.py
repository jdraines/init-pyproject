import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
from skaf.cli import get_args, get_filesystem_template, main


class TestCliArgs:
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_get_args(self, mock_parse_args):
        # Setup mock return value
        mock_args = MagicMock()
        mock_args.name = 'test_project'
        mock_args.template = 'test_template'
        mock_args.path = None
        mock_args.output = '/test/output'
        mock_args.force = False
        mock_args.confirm_defaults = True
        mock_args.debug = False
        mock_parse_args.return_value = mock_args
        mock_args.git = None
        
        # Call function
        args = get_args()
        
        # Verify results
        assert args.name == 'test_project'
        assert args.template == 'test_template'
        assert args.output == '/test/output'
        assert args.force is False
        assert args.confirm_defaults is True
        assert args.debug is False


class TestGetTemplate:
    
    @patch('os.path.isdir')
    @patch('skaf.cli.FilesystemTemplate')
    def test_get_template_valid_path(self, mock_template_class, mock_isdir):
        # Setup mocks
        mock_isdir.return_value = True
        mock_template = MagicMock()
        mock_template.template_name = 'test_template'
        mock_template_class.return_value = mock_template
        
        # Call function
        template = get_filesystem_template('/path/to/test_template')
        
        # Verify results
        mock_isdir.assert_called_once_with('/path/to/test_template')
        mock_template_class.assert_called_once_with('test_template', '/path/to/test_template')
        assert template == mock_template
    
    @patch('os.path.isdir')
    def test_get_template_invalid_path(self, mock_isdir):
        # Setup mock
        mock_isdir.return_value = False
        
        # Call function and verify exception
        with pytest.raises(ValueError) as excinfo:
            get_filesystem_template('/invalid/path')
        
        # Verify error message
        assert "Template path '/invalid/path' is not a valid directory" in str(excinfo.value)


class TestMain:
    
    @patch('skaf.cli.get_args')
    @patch('skaf.cli.get_filesystem_template')
    @patch('skaf.cli.scaffold_project')
    def test_main_success(self, mock_scaffold, mock_get_template, mock_get_args):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.name = 'test_project'
        mock_args.template = 'test_template'
        mock_args.output = '/test/output'
        mock_args.force = False
        mock_args.path = None
        mock_args.auto_use_defaults = None
        mock_args.debug = False
        mock_get_args.return_value = mock_args
        mock_args.git = None
        
        # Call function
        with patch('builtins.print') as mock_print:
            main()
        
        # Verify results
        mock_scaffold.assert_called_once_with(
            project_name='test_project',
            template_name='test_template',
            output_dir='/test/output',
            force=False,
            template=None,
            auto_use_defaults=None,
            _debug = False
        )
        mock_print.assert_called_once_with(
            "Project 'test_project' initialized successfully using the 'test_template' template."
        )
    
    @patch('skaf.cli.get_args')
    @patch('skaf.cli.get_filesystem_template')
    @patch('skaf.cli.scaffold_project')
    def test_main_with_template_path(self, mock_scaffold, mock_get_template, mock_get_args):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.name = 'test_project'
        mock_args.template = None
        mock_args.output = '/test/output'
        mock_args.force = False
        mock_args.path = '/path/to/template'
        mock_args.auto_use_defaults = True
        mock_args.debug = False
        mock_args.git = None
        mock_get_args.return_value = mock_args
        
        mock_template = MagicMock()
        mock_template.template_name = 'custom_template'
        mock_get_template.return_value = mock_template
        
        # Call function
        with patch('builtins.print') as mock_print:
            main()
        
        # Verify results
        mock_get_template.assert_called_once_with('/path/to/template')
        mock_scaffold.assert_called_once_with(
            project_name='test_project',
            template_name='custom_template',
            output_dir='/test/output',
            force=False,
            template=mock_template,
            auto_use_defaults=True,
            _debug=False
        )
        mock_print.assert_called_once_with(
            "Project 'test_project' initialized successfully using the 'custom_template' template."
        )
    
    @patch('skaf.cli.get_args')
    @patch('skaf.cli.scaffold_project')
    def test_main_with_error(self, mock_scaffold, mock_get_args):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.name = 'test_project'
        mock_args.template = 'test_template'
        mock_args.output = '/test/output'
        mock_args.force = False
        mock_args.path = None
        mock_args.confirm_defaults = False
        mock_args.debug = False
        mock_get_args.return_value = mock_args
        mock_args.git = None
        
        mock_scaffold.side_effect = ValueError("Test error")
        
        # Call function
        with patch('builtins.print') as mock_print:
            with patch('sys.exit') as mock_exit:
                main()
        
        # Verify results
        mock_print.assert_called_once_with(
            "An error occurred while initializing the project: ValueError: Test error"
        )
        mock_exit.assert_called_once_with(1)
    
    @patch('skaf.cli.get_args')
    @patch('skaf.cli.scaffold_project')
    def test_main_debug_mode(self, mock_scaffold, mock_get_args):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.name = 'test_project'
        mock_args.template = 'test_template'
        mock_args.output = '/test/output'
        mock_args.force = False
        mock_args.path = None
        mock_args.confirm_defaults = False
        mock_args.debug = True
        mock_get_args.return_value = mock_args
        mock_args.git = None
        
        mock_scaffold.side_effect = ValueError("Test error")
        
        # Call function and verify exception is re-raised
        with pytest.raises(ValueError) as excinfo:
            main()
        
        assert "Test error" in str(excinfo.value)
