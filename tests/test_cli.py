"""Smoke tests for the command-line entry point."""

from canlabel.cli import app


def test_cli_app_is_available() -> None:
    assert app is not None
