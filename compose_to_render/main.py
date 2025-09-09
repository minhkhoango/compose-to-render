# compose_to_render/main.py
"""
The main entrypoint for the CLI application.
"""
from pathlib import Path

import typer
from rich.console import Console

# Create a Typer application instance
app = typer.Typer(
    name="compose-to-render",
    help="Intelligently convert docker-compose.yml to production-ready render.yaml Blueprints",
    add_completion=False
)

# Create a Rich console for beautiful output
console = Console()


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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """
    Converts a docker-compose.yml file to a render.yaml blueprint.
    """
    console.print(f"🚀 Starting conversion of [bold cyan]{input_file.name}[/bold cyan]...")

    # --- TODO: Day 3-7 ---
    # 1. Load the input file using ruamel.yaml and our Pydantic models.
    # 2. Instantiate the Translator class.
    # 3. Call the translate method.
    # 4. Handle potential errors gracefully.
    # 5. Dump the resulting RenderBlueprint object to the output file.
    # 6. Print warnings and success messages using the rich console.
    # ----------------------

    console.print(f"✅ Successfully converted to [bold green]{output_file.name}[/bold green].")


if __name__ == "__main__":
    app()