"""Configuration handling for the Photo Info application."""

from pathlib import Path
from typing import Optional
import tomli
from rich.console import Console

console = Console()

DEFAULT_CONFIG_NAME = "photo_info.toml"

class Config:
    """Configuration handler for Photo Info."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration handler.
        
        Args:
            config_path: Optional path to config file. If None, will look for photo_info.toml
                        in the current directory.
        """
        self.config_path = config_path or Path.cwd() / DEFAULT_CONFIG_NAME
        self.image_dir: Optional[Path] = None
        self.markdown_dir: Optional[Path] = None
        
        if self.config_path.exists():
            self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from TOML file."""
        try:
            with open(self.config_path, "rb") as f:
                config_data = tomli.load(f)
            
            paths = config_data.get("paths", {})
            
            # Convert string paths to Path objects and resolve them relative to config file location
            if "images" in paths:
                self.image_dir = Path(paths["images"]).expanduser()
                if not self.image_dir.is_absolute():
                    self.image_dir = (self.config_path.parent / self.image_dir).resolve()
                else:
                    self.image_dir = self.image_dir.resolve()
            
            if "markdown" in paths:
                self.markdown_dir = Path(paths["markdown"]).expanduser()
                if not self.markdown_dir.is_absolute():
                    self.markdown_dir = (self.config_path.parent / self.markdown_dir).resolve()
                else:
                    self.markdown_dir = self.markdown_dir.resolve()
            
        except Exception as e:
            console.print(f"[red]Error loading config file: {e}[/red]")
            raise

    def validate(self) -> bool:
        """Validate the configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if not self.image_dir or not self.markdown_dir:
            console.print("[red]Error: Both image_dir and markdown_dir must be specified in config[/red]")
            return False
            
        if not self.image_dir.exists():
            console.print(f"[red]Error: Image directory {self.image_dir} does not exist[/red]")
            return False
            
        if not self.markdown_dir.exists():
            console.print(f"[red]Error: Markdown directory {self.markdown_dir} does not exist[/red]")
            return False
            
        return True 