# skaf

## Overview
skaf is a Python tool designed to simplify project scaffolding. It provides a simple interface for defining project templates that can be rendered with minimal effort. Here's a quick guide to installing and making templates:

## Installation

Ensure you have Python 3.10 or above. Install using pip:

```bash
pip install skaf
```

Alternatively, you can clone and install the local package:

```bash
git clone <repository-url>
cd skaf
pip install .
```

## Creating your own templates

1. **Create a template directory**  
   In skaf, templates are directories of files that may or may not contain templating blocks. The default templater is [jinja2](https://jinja.palletsprojects.com/en/stable/), which is a full-featured templating engine with advanced features. *(Note that skaf does not currently use jinja Loaders)*

   Any files that have a `.jinja` file suffix will be rendered. Otherwise, the file will be left as-is.

   All files should be placed in a directory structure that looks like:

   ```
   my-template-root/
      ├── templates/
      │   └── [any files you want]
      └── template_properties.yaml   # this is metadata
   ```

   For example, imagine I want to generate a customized hello world printer that is hard-coded to say hello to a specific person named John. I would create the following file:

   ```jinja
   # my-template-root/templates/hello.py.jinja

   print("Hello {{ some_name }}!")
   ```

2. **Create a `template_properties.yaml`**  
   Next, we can declare metadata about the template. At this point, that primarily looks like declaring a list of variables that might have default values. There are a couple of other optional top-level fields as well:

   ```template_properties.yaml
   templater: jinja2  # default
   auto_use_defaults: false  # default
   custom_variables:
   - name: "some_name"
     type: "str"  # optional
     default: "World"  # optional
     description: Who are we saying hello to?  # optional
   ```

   For custom variables, the `type`, `default`, and `description` fields are optional. Only `name` is required.

   When rendering is run, you will be prompted to enter a value for the `some_name` variable or to accept the default value `World`. If we had instead specified that top-level value `auto_use_defaults: true`, then the templater would run without asking for input, and would provide `World` in as the value for `some_name`. (This particular behavior can also be overridden when invoking the CLI command.)

   The two top-level fields `templater` and `auto_use_defaults` are shown here with default values.


## Command-line Usage

The CLI provides several flags and arguments to customize the initialization of a project with templates:

```bash
skaf <project_name> [options]
```

### Positional Arguments:
- `<project_name>`: The name of the project to create.

### Options:
- `-t, --template <template_name>`: Specify the name of the project template to use.
- `-p, --path <template_directory>`: Provide the path to a local template directory.
- `-o, --output <output_directory>`: Set the output directory for the project. Defaults to the current working directory.
- `-f, --force`: Force overwrite of existing files if they already exist.
- `--auto-use-defaults`: Override the template properties' `auto_use_defaults` with an explicit value here.
- `--debug`: Enable debug mode, which will raise exceptions rather than catching them with a tidier output.

### Example Commands

1. **Creating a project with a template that is included in the package:**
   ```bash
   skaf my_project -t setuptools_pyproject
   ```

2. **Using a local, user-defined template:**
   ```bash
   skaf my_project -p /path/to/my/template
   ```

3. **Defining an Output Directory:**
   ```bash
   skaf my_project -o /path/to/output -p /path/to/my/template
   ```

## Developing Templates

To create and use custom templates in skaf, follow these steps:

1. **Directory Setup**:
   - In skaf, templates are directories of files that contain templating blocks.
     Custom templates can be created in an location on your local machine and should have
     the following structure:

     ```
     my-template-root/
        ├── templates/
        │   └── [any files you want]
        └── template_properties.yaml   # this is metadata
     ```

2. **template_properties.yaml**:
   - Define custom variables and the templating engine to use.
   - Example properties:
     ```yaml
     custom_variables:
       - name: "author_name"
         type: "string"
         default: "John Doe"
         description: "The name of the project author."
     templater: "jinja2"
     ```

3. **Render your template**
   - Run the following command:
     ```bash
     skaf my-project --path path/to/my-template-root
     ```

## Development Dependencies

To contribute or run tests, install development dependencies:

```bash
pip install .[dev]
```

## Contribute

If you find a bug or have a feature request, please file an [issue](https://github.com/jdraines/skaf/issues).
