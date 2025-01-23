"""Entry point for the application."""

# photo_info/__main__.py

from src import cli, __app_name__


def main() -> None:
    """Run the CLI."""
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
