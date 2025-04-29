# init_pyproject/cli.py
import os
import sys
from .scaffold import scaffold_project
from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser(description="Initialize a new Python project with a pyproject.toml file.")
    parser.add_argument("name", help="The name of the project to create.")
    parser.add_argument("--template", default="setuptools", help="Name of the project template to use.")
    return parser.parse_args()


def main():
    args = get_args()
    project_name = args.name
    template_name = args.template

    try:
        scaffold_project(project_name, template_name)
        print(f"Project '{project_name}' initialized successfully using the '{template_name}' template.")
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while initializing the project: {e}")
        sys.exit(1)
