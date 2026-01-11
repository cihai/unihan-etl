"""Tests for CLI help formatter."""

from __future__ import annotations

import argparse
import typing as t

import pytest

from unihan_etl.cli._colors import ColorMode, Colors
from unihan_etl.cli._formatter import (
    HelpTheme,
    create_themed_formatter,
)


class FormatterCreationFixture(t.NamedTuple):
    """Test fixture for formatter creation."""

    test_id: str
    color_mode: ColorMode
    expect_colored: bool


FORMATTER_CREATION_FIXTURES: list[FormatterCreationFixture] = [
    FormatterCreationFixture(
        test_id="always_mode_colored",
        color_mode=ColorMode.ALWAYS,
        expect_colored=True,
    ),
    FormatterCreationFixture(
        test_id="never_mode_plain",
        color_mode=ColorMode.NEVER,
        expect_colored=False,
    ),
]


@pytest.mark.parametrize(
    FormatterCreationFixture._fields,
    FORMATTER_CREATION_FIXTURES,
    ids=[f.test_id for f in FORMATTER_CREATION_FIXTURES],
)
def test_create_themed_formatter(
    test_id: str,
    color_mode: ColorMode,
    expect_colored: bool,
) -> None:
    """Test themed formatter creation with different color modes."""
    colors = Colors(color_mode)
    formatter_class = create_themed_formatter(colors)

    # Create a parser with the formatter
    # Use description with examples to trigger colorization
    parser = argparse.ArgumentParser(
        prog="test-prog",
        description="Test description.\n\nexamples:\n  test-prog --help",
        formatter_class=formatter_class,
    )
    parser.add_argument("--test", help="Test option")

    # Get help text
    help_text = parser.format_help()

    # Verify formatter produces output
    assert "test-prog" in help_text
    assert "Test description" in help_text

    if expect_colored:
        # ANSI escape codes should be present in example lines
        assert "\x1b[" in help_text
    else:
        # No ANSI escape codes
        assert "\x1b[" not in help_text


class HelpThemeFixture(t.NamedTuple):
    """Test fixture for HelpTheme creation."""

    test_id: str
    prog: str
    action: str
    long_option: str


HELP_THEME_FIXTURES: list[HelpThemeFixture] = [
    HelpThemeFixture(
        test_id="default_theme",
        prog="cyan_prog",
        action="green_action",
        long_option="yellow_opt",
    ),
    HelpThemeFixture(
        test_id="custom_theme",
        prog="magenta_prog",
        action="blue_action",
        long_option="red_opt",
    ),
]


@pytest.mark.parametrize(
    HelpThemeFixture._fields,
    HELP_THEME_FIXTURES,
    ids=[f.test_id for f in HELP_THEME_FIXTURES],
)
def test_help_theme_creation(
    test_id: str,
    prog: str,
    action: str,
    long_option: str,
) -> None:
    """Test HelpTheme namedtuple creation."""
    theme = HelpTheme(
        prog=prog,
        action=action,
        long_option=long_option,
        short_option="short",
        label="label",
        heading="heading",
        reset="reset",
    )
    assert theme.prog == prog
    assert theme.action == action
    assert theme.long_option == long_option


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
    colors = Colors(ColorMode.NEVER)
    formatter_class = create_themed_formatter(colors)

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
    colors = Colors(ColorMode.NEVER)
    formatter_class = create_themed_formatter(colors)

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
    colors = Colors(ColorMode.NEVER)
    formatter_class = create_themed_formatter(colors)

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
