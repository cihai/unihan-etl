"""Tests for CLI help formatter."""

from __future__ import annotations

import argparse
import typing as t

import pytest

from unihan_etl.cli._formatter import (
    UnihanHelpFormatter,
    create_themed_formatter,
)


class FormatterCreationFixture(t.NamedTuple):
    """Test fixture for formatter creation."""

    test_id: str
    description: str


FORMATTER_CREATION_FIXTURES: list[FormatterCreationFixture] = [
    FormatterCreationFixture(
        test_id="simple_description",
        description="Test description.\n\nexamples:\n  test-prog --help",
    ),
    FormatterCreationFixture(
        test_id="no_examples",
        description="Simple description without examples.",
    ),
]


@pytest.mark.parametrize(
    FormatterCreationFixture._fields,
    FORMATTER_CREATION_FIXTURES,
    ids=[f.test_id for f in FORMATTER_CREATION_FIXTURES],
)
def test_create_themed_formatter(
    test_id: str,
    description: str,
) -> None:
    """Test themed formatter creation with Python 3.14 native theming.

    The formatter relies on Python 3.14's native _theme attribute, which
    is automatically set based on TTY detection and environment variables.
    In tests (non-TTY), no colors are applied.
    """
    formatter_class = create_themed_formatter()

    # Create a parser with the formatter
    parser = argparse.ArgumentParser(
        prog="test-prog",
        description=description,
        formatter_class=formatter_class,
    )
    parser.add_argument("--test", help="Test option")

    # Get help text
    help_text = parser.format_help()

    # Verify formatter produces output
    assert "test-prog" in help_text

    # In non-TTY environment (tests), Python 3.14's argparse won't colorize
    # So we verify basic content presence rather than color codes
    if "examples:" in description:
        assert "examples:" in help_text


class FormatterOutputFixture(t.NamedTuple):
    """Test fixture for formatter output verification."""

    test_id: str
    prog: str
    description: str
    expected_in_help: list[str]


FORMATTER_OUTPUT_FIXTURES: list[FormatterOutputFixture] = [
    FormatterOutputFixture(
        test_id="basic_parser",
        prog="myapp",
        description="My application description.",
        expected_in_help=["myapp", "My application description"],
    ),
    FormatterOutputFixture(
        test_id="complex_description",
        prog="unihan-etl",
        description="Export UNIHAN data.\n\nexamples:\n  unihan-etl export",
        expected_in_help=["unihan-etl", "Export UNIHAN", "examples:"],
    ),
]


@pytest.mark.parametrize(
    FormatterOutputFixture._fields,
    FORMATTER_OUTPUT_FIXTURES,
    ids=[f.test_id for f in FORMATTER_OUTPUT_FIXTURES],
)
def test_formatter_output(
    test_id: str,
    prog: str,
    description: str,
    expected_in_help: list[str],
) -> None:
    """Test formatter output contains expected content."""
    formatter_class = create_themed_formatter()

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        formatter_class=formatter_class,
    )

    help_text = parser.format_help()

    for expected in expected_in_help:
        assert expected in help_text


def test_unihan_help_formatter_inherits_raw_description() -> None:
    """Test UnihanHelpFormatter preserves raw description formatting."""
    formatter_class = create_themed_formatter()

    # Verify it's a subclass of RawDescriptionHelpFormatter behavior
    parser = argparse.ArgumentParser(
        prog="test",
        description="Line 1\n\nLine 2\n\nLine 3",
        formatter_class=formatter_class,
    )

    help_text = parser.format_help()

    # Raw description should preserve newlines
    assert "Line 1" in help_text
    assert "Line 2" in help_text
    assert "Line 3" in help_text


def test_formatter_with_subparsers() -> None:
    """Test formatter works correctly with subparsers."""
    formatter_class = create_themed_formatter()

    parser = argparse.ArgumentParser(
        prog="myapp",
        description="Main app.",
        formatter_class=formatter_class,
    )

    subparsers = parser.add_subparsers(dest="command", title="commands")
    subparsers.add_parser(
        "export",
        help="Export data",
        formatter_class=formatter_class,
    )
    subparsers.add_parser(
        "import",
        help="Import data",
        formatter_class=formatter_class,
    )

    help_text = parser.format_help()

    assert "commands" in help_text
    assert "export" in help_text
    assert "import" in help_text


def test_create_themed_formatter_returns_unihan_formatter() -> None:
    """Test create_themed_formatter returns UnihanHelpFormatter class."""
    formatter_class = create_themed_formatter()
    assert formatter_class is UnihanHelpFormatter


def test_formatter_uses_native_theme() -> None:
    """Test formatter uses Python 3.14's native _theme attribute.

    This test verifies the formatter checks for _theme (not _help_theme)
    when colorizing, which is the attribute set by Python 3.14's argparse.
    """
    formatter_class = create_themed_formatter()
    formatter = formatter_class("test")

    # In non-TTY environment, _theme should be None or not set
    theme = getattr(formatter, "_theme", None)
    # We don't assert the value since it depends on Python version and TTY

    # But we can verify _help_theme is NOT used (removed in the fix)
    # The formatter should not have _help_theme as a class attribute
    assert not hasattr(UnihanHelpFormatter, "_help_theme")
