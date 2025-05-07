import sys
import os
from pathlib import Path
from .scaffold import scaffold_project
from argparse import ArgumentParser
from .template_classes.filesystem_template import FilesystemTemplate
from .template_classes.git_template import GitTemplate


def get_args():
    parser = ArgumentParser(description="Run the templater to build out a project file structure from templates.")
    parser.add_argument("name", help="The name of the project to create.")
    parser.add_argument("-t", "--template", default=None, help="Name of the project template to use.")
    parser.add_argument("-p", "--path", default=None, help="Path to a template directory.")
    parser.add_argument("-g", "--git", default=None, help="URI of a git repo to be used as a template directory.")
    parser.add_argument("-o", "--output", help="Output directory for the project.", default=os.getcwd())
    parser.add_argument("-f", "--force", action="store_true", help="Force overwrite existing files.")
    parser.add_argument("--auto-use-defaults", action="store_true", help="Automatically use default values for template variables if present. (Overrides the template properties field of the same name.)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()
    if args.auto_use_defaults is False:
        args.auto_use_defaults = None  # tracks only explicit True
    return args


def get_filesystem_template(template_path) -> FilesystemTemplate:
    """
    Get a template from the filesystem.
    """
    if os.path.isdir(template_path):
        template_name = Path(template_path).name
        template = FilesystemTemplate(template_name, template_path)
        return template
    else:
        raise ValueError(f"Template path '{template_path}' is not a valid directory.")


def get_git_template(git_uri) -> GitTemplate:
    """
    Get a template from a git repository.
    """
    template_name = Path(git_uri).name
    return GitTemplate(template_name, git_uri)


def main():
    args = get_args()
    project_name = args.name
    template_name = args.template
    output_dir = args.output
    force = args.force
    template_path = args.path

    template = None
    if template_path:
        template = get_filesystem_template(template_path)
        template_name = template.template_name
    elif args.git:
        template = get_git_template(args.git)
        template_name = template.template_name

    try:
        scaffold_project(
            project_name=project_name,
            template_name=template_name,
            output_dir=output_dir,
            force=force,
            template=template,
            auto_use_defaults=args.auto_use_defaults,
            _debug=args.debug
            )
        print(f"Project '{project_name}' initialized successfully using the '{template_name}' template.")
    except Exception as e:
        if args.debug:
            raise
        etype = type(e).__name__
        print(f"An error occurred while initializing the project: {etype}: {e}")
        sys.exit(1)
