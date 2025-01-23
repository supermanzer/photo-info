"""Creating the CLI for th Photo Info project."""

# photo_info/cli.py


from typing import Optional

import typer

from photo_info import __app_name__, __version__

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Print application name and version information.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
