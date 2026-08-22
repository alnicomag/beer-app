"""Command-line interface for Can Label Lab."""

import typer

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Run Can Label Lab experiments."""
