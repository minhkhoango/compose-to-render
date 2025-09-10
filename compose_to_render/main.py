# compose_to_render/main.py
"""
The main entrypoint for the CLI application.
"""
from pathlib import Path
import sys

import typer
from typing import Dict, Any, List, Tuple
from rich.console import Console
from ruamel.yaml import YAML
from dataclasses import asdict

from .models import DockerComposeConfig, DockerComposeService
from .translator import Translator

# Create a Typer application instance
app = typer.Typer(
    name="compose-to-render",
    help="Intelligently convert docker-compose.yml to production-ready render.yaml Blueprints",
    add_completion=False
)

# Create a Rich console for beautiful output
console = Console()
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def clean_dict_factory(data: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """
    Custom dict factory for asdict that filters out fields with a value of None.
    This keeps the output YAML clean and readable.
    """
    return {k: v for k, v in data if v is not None}

@app.command()
def convert(
    input_file: Path = typer.Option(
        "docker-compose.yml",
        "--input",
        "-i",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the input docker-compose.yml file.",
    ),
    output_file: Path = typer.Option(
        "render.yaml",
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        help="Path to the output render.yaml file.",
    ),
) -> None:
    """
    Converts a docker-compose.yml file to a render.yaml blueprint.
    """
    console.print(f"🚀 Starting conversion of [bold cyan]{input_file.name}[/bold cyan]...")

    try:
        with open(input_file, 'r') as f:
            data = yaml.load(f)

        # Basic validation
        if 'services' not in data:
            raise ValueError("Input file must contain a 'services' key.")

        # Manually deserialize into our dataclasses
        services_data: Dict[str, Dict[str, Any]] = data.get('services', {})
        services: Dict[str, DockerComposeService] = {
            name: DockerComposeService(**(service_data or {}))
            for name, service_data in services_data.items()
        }
        volumes_data = data.get('volumes', {})
        compose_config = DockerComposeConfig(services=services, volumes=volumes_data)

        # The core logic
        translator = Translator(compose_config)
        blueprint = translator.translate()

        # Prepare the output data
        blueprint_dict = asdict(blueprint, dict_factory=clean_dict_factory)


        with open(output_file, 'w') as f:
            yaml.dump(blueprint_dict, f)

        console.print(f"✅ Successfully converted to [bold green]{output_file.name}[/bold green].")

        # Print warnings, if any
        if translator.warnings:
            console.print("\n⚠️ [bold yellow]Warnings:[/bold yellow]")
            for warning in translator.warnings:
                console.print(f"  - {warning}")
    
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()