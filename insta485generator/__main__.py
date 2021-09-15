"""Build static HTML site from directory of HTML templates and plain files."""
import os
import pathlib
import json
import sys
import shutil
import click
import jinja2


class Env:
    """Stores all neccesary environment variables."""

    def __init__(self):
        """Initialize member variables."""
        self.input_dir = None
        self.templates_dir = None
        self.output_dir = None
        self.verbose = False
        self.env = None

    def set_input_dir(self, input_dir):
        """Set input directory."""
        self.input_dir = input_dir if input_dir[-1] == '/' else input_dir + '/'

        if not os.path.isdir(self.input_dir):
            print("Invalid input directory!")
            sys.exit(1)

    def set_template_dir(self, templates_dir):
        """Set template directory."""
        self.templates_dir = templates_dir

    def set_output_dir(self, out):
        """Set output directory."""
        if out is None:
            out = self.input_dir + "html"
        else:
            out = str(click.format_filename(out))
        self.output_dir = out if out[-1] == '/' else out + '/'

        if os.path.isdir(self.output_dir):
            print("Error: Output directory already exists")
            sys.exit(1)

    def set_verbose(self, verbose):
        """Set verbose flag."""
        self.verbose = verbose

    def set_env(self, env):
        """Set environment."""
        self.env = env


ENV = Env()


def fill_template():
    """Fill template with HTML information."""
    config_dict = None

    try:
        with open(ENV.input_dir + "config.json") as json_file:
            config_dict = json.load(json_file)

    except FileNotFoundError:
        print("No such file config.json!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Json error!")
        sys.exit(1)

    input_dir = pathlib.Path(ENV.input_dir)
    output_dir = pathlib.Path(ENV.output_dir)
    static_path = input_dir/"static"
    if os.path.isdir(static_path):
        shutil.copytree(input_dir/"static", output_dir)

        # for file in static_content:
        #     shutil.copytree(static_path/file, dest)
        #     os.replace(static_path/file, output_dir/file)

        if ENV.verbose:
            print(f'Copied {static_path} -> {output_dir}')

    for item in config_dict:
        url = item['url']
        template_filename = item['template']
        context = item['context']
        try:
            template = ENV.env.get_template(template_filename)
            filled = template.render(**context)
            write_output(filled, url)
        except jinja2.TemplateSyntaxError:
            print("Syntax error!")
            sys.exit(1)
        except jinja2.TemplateNotFound:
            print("Template not found!")
            sys.exit(1)
        except jinja2.TemplateError:
            print("Template error")
            sys.exit(1)


def write_output(filled, url):
    """Write output to correct file."""
    url = url.lstrip("/")
    output_dir = pathlib.Path(ENV.output_dir)
    output_dir_url = output_dir/url
    output_path = output_dir_url/"index.html"
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if not os.path.exists(output_dir/url):
        os.makedirs(output_dir/url, exist_ok=True)
    try:
        with open(output_path, "w") as file_out:
            file_out.write(filled)
            print(f'Rendered index.html -> { output_path }')
    except FileNotFoundError:
        print("Output file not found")
        sys.exit(1)


@click.command()
@click.argument("INPUT_DIR", type=click.Path(exists=True), required=True)
@click.option("-o", "--output",
              type=click.Path(exists=False), help="Output directory.")
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def cli(input_dir, output=None, verbose=False):
    """Templated static website generator."""
    inputdir = str(click.format_filename(input_dir))

    ENV.set_input_dir(inputdir)

    templatedir = ENV.input_dir + "templates"

    ENV.set_template_dir(templatedir)

    ENV.set_output_dir(output)

    ENV.set_verbose(verbose)

    try:
        template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templatedir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
        )
    except jinja2.TemplateSyntaxError:
        print("Syntax error!")
        sys.exit(1)
    except jinja2.TemplateNotFound:
        print("Template not found!")
        sys.exit(1)
    except jinja2.TemplateError:
        print("Template error")
        sys.exit(1)

    ENV.set_env(template_env)

    fill_template()


def main():
    """Top level command line interface."""
    cli()


if __name__ == "__main__":
    main()
