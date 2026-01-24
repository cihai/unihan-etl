"""Custom help formatter for unihan-etl CLI with colorized examples.

This module provides a custom argparse formatter that colorizes example
sections in help output, similar to tmuxp/vcspull's formatter.

Examples
--------
>>> from unihan_etl.cli._formatter import UnihanHelpFormatter
>>> UnihanHelpFormatter  # doctest: +ELLIPSIS
<class '...UnihanHelpFormatter'>
"""

from __future__ import annotations

import argparse
import re
import typing as t

# Options that expect a value (set externally or via --option=value)
OPTIONS_EXPECTING_VALUE = frozenset(
    {
        "-f",
        "--fields",
        "-F",
        "--format",
        "-d",
        "--destination",
        "-s",
        "--source",
        "-z",
        "--zip-path",
        "-w",
        "--work-dir",
        "-i",
        "--input-files",
        "-l",
        "--log-level",
        "-o",
        "--output",
        "--cache-dir",
    }
)

# Standalone flag options (no value)
OPTIONS_FLAG_ONLY = frozenset(
    {
        "-h",
        "--help",
        "-V",
        "--version",
        "-v",
        "--verbose",
        "--no-expand",
        "--no-prune",
        "--no-cache",
        "--json",
        "--ndjson",
        "--with-fields",
    }
)


class UnihanHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Help formatter with colorized examples for unihan-etl CLI.

    This formatter extends RawDescriptionHelpFormatter to preserve formatting
    of description text while adding syntax highlighting to example sections.

    The formatter uses Python 3.14's native `_theme` attribute for colorization.
    If no theme is set (non-TTY or NO_COLOR), the formatter falls back to plain text.

    Examples
    --------
    >>> formatter = UnihanHelpFormatter("unihan-etl")
    >>> formatter  # doctest: +ELLIPSIS
    <...UnihanHelpFormatter object at ...>
    """

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        """Fill text, colorizing examples sections if theme is available.

        Parameters
        ----------
        text : str
            Text to format.
        width : int
            Maximum line width.
        indent : str
            Indentation prefix.

        Returns
        -------
        str
            Formatted text, with colorized examples if theme is set.

        Examples
        --------
        Without theme, returns text via parent formatter:

        >>> formatter = UnihanHelpFormatter("test")
        >>> formatter._fill_text("hello", 80, "")
        'hello'
        """
        theme = getattr(self, "_theme", None)
        if not text or theme is None:
            return super()._fill_text(text, width, indent)

        lines = text.splitlines(keepends=True)
        formatted_lines: list[str] = []
        in_examples_block = False
        expect_value = False

        for line in lines:
            if line.strip() == "":
                # Keep in_examples_block active across blank lines so category
                # headings like "Download:" stay colorized after "examples:"
                expect_value = False
                formatted_lines.append(f"{indent}{line}")
                continue

            has_newline = line.endswith("\n")
            stripped_line = line.rstrip("\n")
            leading_length = len(stripped_line) - len(stripped_line.lstrip(" "))
            leading = stripped_line[:leading_length]
            content = stripped_line[leading_length:]
            content_lower = content.lower()
            # Recognize example section headings:
            # - "examples:" starts the examples block
            # - "X examples:" or "X:" are sub-section headings within examples
            is_examples_start = content_lower == "examples:"
            is_category_in_block = (
                in_examples_block and content.endswith(":") and not content[0].isspace()
            )
            is_section_heading = (
                content_lower.endswith("examples:") or is_category_in_block
            ) and not is_examples_start

            if is_section_heading or is_examples_start:
                formatted_content = f"{theme.heading}{content}{theme.reset}"
                in_examples_block = True
                expect_value = False
            elif in_examples_block:
                colored_content = self._colorize_example_line(
                    content,
                    theme=theme,
                    expect_value=expect_value,
                )
                expect_value = colored_content.expect_value
                formatted_content = colored_content.text
            else:
                formatted_content = content

            newline = "\n" if has_newline else ""
            formatted_lines.append(f"{indent}{leading}{formatted_content}{newline}")

        return "".join(formatted_lines)

    class _ColorizedLine(t.NamedTuple):
        """Result of colorizing an example line."""

        text: str
        expect_value: bool

    def _colorize_example_line(
        self,
        content: str,
        *,
        theme: t.Any,
        expect_value: bool,
    ) -> _ColorizedLine:
        """Colorize a single example command line.

        Parameters
        ----------
        content : str
            The line content to colorize.
        theme : Any
            Theme object with color attributes (prog, action, etc.).
        expect_value : bool
            Whether the previous token expects a value.

        Returns
        -------
        _ColorizedLine
            Named tuple with colorized text and updated expect_value state.

        Examples
        --------
        With an empty theme (no colors), returns text unchanged:

        >>> formatter = UnihanHelpFormatter("test")
        >>> from types import SimpleNamespace
        >>> theme = SimpleNamespace(
        ...     prog="", action="", long_option="", short_option="",
        ...     label="", heading="", reset=""
        ... )
        >>> result = formatter._colorize_example_line(
        ...     "unihan-etl export", theme=theme, expect_value=False
        ... )
        >>> result.text
        'unihan-etl export'
        >>> result.expect_value
        False
        """
        parts: list[str] = []
        expecting_value = expect_value
        first_token = True
        colored_subcommand = False

        for match in re.finditer(r"\s+|\S+", content):
            token = match.group()
            if token.isspace():
                parts.append(token)
                continue

            if expecting_value:
                color = theme.label
                expecting_value = False
            elif token.startswith("--"):
                color = theme.long_option
                expecting_value = (
                    token not in OPTIONS_FLAG_ONLY and token in OPTIONS_EXPECTING_VALUE
                )
            elif token.startswith("-"):
                color = theme.short_option
                expecting_value = (
                    token not in OPTIONS_FLAG_ONLY and token in OPTIONS_EXPECTING_VALUE
                )
            elif first_token:
                color = theme.prog
            elif not colored_subcommand:
                color = theme.action
                colored_subcommand = True
            else:
                color = None

            first_token = False

            if color:
                parts.append(f"{color}{token}{theme.reset}")
            else:
                parts.append(token)

        return self._ColorizedLine(text="".join(parts), expect_value=expecting_value)


def create_themed_formatter() -> type[UnihanHelpFormatter]:
    """Create a help formatter class.

    The formatter uses Python 3.14's native _theme attribute for colorization.
    We don't inject our own theme - argparse handles this automatically based
    on TTY detection and environment variables (NO_COLOR, FORCE_COLOR).

    Returns
    -------
    type[UnihanHelpFormatter]
        Formatter class that uses Python's native theme support.

    Examples
    --------
    >>> from unihan_etl.cli._formatter import create_themed_formatter

    Create formatter (uses Python 3.14 native theming):

    >>> formatter_cls = create_themed_formatter()
    >>> formatter = formatter_cls("test")
    >>> formatter  # doctest: +ELLIPSIS
    <...UnihanHelpFormatter object at ...>
    """
    # Simply return the formatter class - Python 3.14 handles theming
    return UnihanHelpFormatter


__all__ = [
    "UnihanHelpFormatter",
    "create_themed_formatter",
]
