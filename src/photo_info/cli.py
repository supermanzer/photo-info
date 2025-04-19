"""Command-line interface for the Photo Info application."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from photo_info import __version__, photo_info
from photo_info.config import Config

app = typer.Typer(
    name="photo-info",
    help="Extract EXIF metadata from photos and generate markdown files",
    add_completion=False,
)
console = Console()

def version_callback(value: bool):
    """Print the version of the application."""
    if value:
        console.print(Panel.fit(f"Photo Info v{__version__}"))
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file. Defaults to photo_info.toml in current directory.",
    )
):
    """Photo Info - Extract EXIF metadata from photos and generate markdown files."""
    pass

@app.command()
def process(
    image_dir: Optional[Path] = typer.Argument(
        None,
        help="Directory containing the images to process. If not provided, uses config file.",
        exists=False,
    ),
    md_dir: Optional[Path] = typer.Argument(
        None,
        help="Directory where markdown files will be saved. If not provided, uses config file.",
        exists=False,
    ),
):
    """Process images in the specified directory and generate markdown files with EXIF data."""
    try:
        # Load configuration
        config = Config()
        
        # Override config with command line arguments if provided
        if image_dir:
            config.image_dir = image_dir
        if md_dir:
            config.markdown_dir = md_dir
            
        # Validate configuration
        if not config.validate():
            raise typer.Exit(code=1)
            
        # Ensure directories end with a slash for compatibility with existing code
        image_dir_str = str(config.image_dir) + "/"
        md_dir_str = str(config.markdown_dir) + "/"
        
        new_images = photo_info.identify_new_images(image_dir_str, md_dir_str)
        
        if not new_images:
            console.print("[yellow]No new images found to process.[/yellow]")
            return
            
        console.print(f"[green]Found {len(new_images)} new images to process[/green]")
        
        for image_name in new_images:
            image_file = image_dir_str + image_name + ".jpg"
            console.print(f"Processing {image_name}...")
            
            exif_data = photo_info.get_exif_data(image_file)
            labeled_exif = photo_info.get_labeled_exif(exif_data)
            photo_info.write_to_markdown(image_file, labeled_exif, md_dir_str)
            
        console.print("[green]Successfully processed all images![/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def init():
    """Initialize a new configuration file in the current directory."""
    config_path = Path.cwd() / "photo_info.toml"
    if config_path.exists():
        console.print("[yellow]Configuration file already exists.[/yellow]")
        raise typer.Exit(code=1)
        
    config_content = """# Photo Info Configuration

[paths]
# Paths can be absolute or relative to this config file
images = "images"     # Directory containing images to process
markdown = "markdown" # Directory where markdown files will be saved
"""
    
    try:
        config_path.write_text(config_content)
        console.print("[green]Created configuration file: photo_info.toml[/green]")
        console.print("Edit the file to set your image and markdown directories.")
        return 0
    except Exception as e:
        console.print(f"[red]Error creating configuration file: {e}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
