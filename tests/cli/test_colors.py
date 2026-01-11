"""Tests for CLI color infrastructure."""

from __future__ import annotations

import typing as t

import pytest

from unihan_etl.cli._colors import (
    ColorMode,
    Colors,
    build_description,
    get_color_mode,
    style,
)


class ColorModeFixture(t.NamedTuple):
    """Test fixture for color mode parsing."""

    test_id: str
    input_value: str
    expected_mode: ColorMode


COLOR_MODE_FIXTURES: list[ColorModeFixture] = [
    ColorModeFixture(
        test_id="auto_mode",
        input_value="auto",
        expected_mode=ColorMode.AUTO,
    ),
    ColorModeFixture(
        test_id="always_mode",
        input_value="always",
        expected_mode=ColorMode.ALWAYS,
    ),
    ColorModeFixture(
        test_id="never_mode",
        input_value="never",
        expected_mode=ColorMode.NEVER,
    ),
    ColorModeFixture(
        test_id="unknown_defaults_to_auto",
        input_value="invalid",
        expected_mode=ColorMode.AUTO,
    ),
]


@pytest.mark.parametrize(
    ColorModeFixture._fields,
    COLOR_MODE_FIXTURES,
    ids=[f.test_id for f in COLOR_MODE_FIXTURES],
)
def test_get_color_mode(
    test_id: str,
    input_value: str,
    expected_mode: ColorMode,
) -> None:
    """Test color mode parsing from string."""
    result = get_color_mode(input_value)
    assert result == expected_mode


class StyleFixture(t.NamedTuple):
    """Test fixture for style function."""

    test_id: str
    text: str
    fg: str
    bold: bool
    expected_contains: list[str]


STYLE_FIXTURES: list[StyleFixture] = [
    StyleFixture(
        test_id="green_text",
        text="hello",
        fg="green",
        bold=False,
        expected_contains=["32m", "hello", "\x1b[0m"],
    ),
    StyleFixture(
        test_id="red_bold_text",
        text="error",
        fg="red",
        bold=True,
        expected_contains=["31m", "1m", "error", "\x1b[0m"],
    ),
    StyleFixture(
        test_id="cyan_text",
        text="info",
        fg="cyan",
        bold=False,
        expected_contains=["36m", "info", "\x1b[0m"],
    ),
]


@pytest.mark.parametrize(
    StyleFixture._fields,
    STYLE_FIXTURES,
    ids=[f.test_id for f in STYLE_FIXTURES],
)
def test_style(
    test_id: str,
    text: str,
    fg: str,
    bold: bool,
    expected_contains: list[str],
) -> None:
    """Test style function produces ANSI escape codes."""
    result = style(text, fg=fg, bold=bold)
    for expected in expected_contains:
        assert expected in result


class ColorMethodFixture(t.NamedTuple):
    """Test fixture for Colors class methods."""

    test_id: str
    method_name: str
    input_text: str


COLOR_METHOD_FIXTURES: list[ColorMethodFixture] = [
    ColorMethodFixture(
        test_id="success_method",
        method_name="success",
        input_text="OK",
    ),
    ColorMethodFixture(
        test_id="error_method",
        method_name="error",
        input_text="FAIL",
    ),
    ColorMethodFixture(
        test_id="warning_method",
        method_name="warning",
        input_text="WARN",
    ),
    ColorMethodFixture(
        test_id="info_method",
        method_name="info",
        input_text="INFO",
    ),
    ColorMethodFixture(
        test_id="highlight_method",
        method_name="highlight",
        input_text="HIGHLIGHT",
    ),
    ColorMethodFixture(
        test_id="muted_method",
        method_name="muted",
        input_text="MUTED",
    ),
]


@pytest.mark.parametrize(
    ColorMethodFixture._fields,
    COLOR_METHOD_FIXTURES,
    ids=[f.test_id for f in COLOR_METHOD_FIXTURES],
)
def test_colors_always_applies_color(
    colors_always: Colors,
    test_id: str,
    method_name: str,
    input_text: str,
) -> None:
    """Test Colors methods apply color in ALWAYS mode."""
    method = getattr(colors_always, method_name)
    result = method(input_text)
    # Should contain ANSI escape codes
    assert "\x1b[" in result
    assert input_text in result


@pytest.mark.parametrize(
    ColorMethodFixture._fields,
    COLOR_METHOD_FIXTURES,
    ids=[f.test_id for f in COLOR_METHOD_FIXTURES],
)
def test_colors_never_returns_plain(
    colors_never: Colors,
    test_id: str,
    method_name: str,
    input_text: str,
) -> None:
    """Test Colors methods return plain text in NEVER mode."""
    method = getattr(colors_never, method_name)
    result = method(input_text)
    # Should be plain text, no ANSI codes
    assert result == input_text
    assert "\x1b[" not in result


class BuildDescriptionFixture(t.NamedTuple):
    """Test fixture for build_description function."""

    test_id: str
    intro: str
    example_blocks: tuple[tuple[str | None, list[str]], ...]
    expected_contains: list[str]


BUILD_DESCRIPTION_FIXTURES: list[BuildDescriptionFixture] = [
    BuildDescriptionFixture(
        test_id="simple_intro_only",
        intro="Simple description.",
        example_blocks=(),
        expected_contains=["Simple description."],
    ),
    BuildDescriptionFixture(
        test_id="intro_with_unnamed_examples",
        intro="Tool description.",
        example_blocks=((None, ["cmd --help", "cmd run"]),),
        expected_contains=["Tool description.", "examples:", "cmd --help", "cmd run"],
    ),
    BuildDescriptionFixture(
        test_id="intro_with_named_section",
        intro="Tool description.",
        example_blocks=(("Export", ["cmd export"]),),
        expected_contains=["Tool description.", "Export:", "cmd export"],
    ),
    BuildDescriptionFixture(
        test_id="multiple_sections",
        intro="Main intro.",
        example_blocks=(
            ("Section A", ["cmd a"]),
            ("Section B", ["cmd b"]),
        ),
        expected_contains=["Main intro.", "Section A:", "cmd a", "Section B:", "cmd b"],
    ),
]


@pytest.mark.parametrize(
    BuildDescriptionFixture._fields,
    BUILD_DESCRIPTION_FIXTURES,
    ids=[f.test_id for f in BUILD_DESCRIPTION_FIXTURES],
)
def test_build_description(
    test_id: str,
    intro: str,
    example_blocks: tuple[tuple[str | None, list[str]], ...],
    expected_contains: list[str],
) -> None:
    """Test build_description generates expected help text."""
    result = build_description(intro, example_blocks)
    for expected in expected_contains:
        assert expected in result


def test_colors_enabled_in_always_mode() -> None:
    """Test colors are enabled in ALWAYS mode."""
    colors = Colors(ColorMode.ALWAYS)
    assert colors._enabled is True
    assert colors.mode == ColorMode.ALWAYS


def test_colors_disabled_in_never_mode() -> None:
    """Test colors are disabled in NEVER mode."""
    colors = Colors(ColorMode.NEVER)
    assert colors._enabled is False
    assert colors.mode == ColorMode.NEVER
