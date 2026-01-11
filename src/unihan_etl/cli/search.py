"""Search subcommand for unihan-etl CLI.

This module provides the search subcommand that looks up UNIHAN
character data by character, UCN, or hex codepoint.
"""

from __future__ import annotations

import logging
import re
import sys
import typing as t

from unihan_etl.cli._colors import build_description
from unihan_etl.cli._output import (
    OutputFormat,
    add_output_arguments,
    get_output_format_from_args,
    print_output,
)
from unihan_etl.core import Packager
from unihan_etl.options import Options
from unihan_etl.util import ucn_to_unicode

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction

log = logging.getLogger(__name__)


SEARCH_DESCRIPTION = build_description(
    """Search and look up UNIHAN characters.

Look up character data by character, UCN (U+XXXX), or hex codepoint.
Requires UNIHAN data to be downloaded (will download if not cached).""",
    (
        (
            None,
            [
                "unihan-etl search 一",
                "unihan-etl search U+4E00",
                "unihan-etl search 4E00",
            ],
        ),
        (
            "Output formats",
            [
                "unihan-etl search 一 --json",
                "unihan-etl search 一 --ndjson",
            ],
        ),
        (
            "Field filtering",
            [
                "unihan-etl search 一 -f kDefinition kMandarin",
            ],
        ),
    ),
)


def create_search_subparser(
    subparsers: _SubParsersAction[ArgumentParser],
    formatter_class: type[t.Any] | None = None,
) -> ArgumentParser:
    """Create and configure the search subcommand parser.

    Parameters
    ----------
    subparsers : _SubParsersAction
        Subparser action from parent parser.
    formatter_class : type | None
        Optional formatter class for help output.

    Returns
    -------
    ArgumentParser
        Configured search subcommand parser.
    """
    parser_kwargs: dict[str, t.Any] = {
        "help": "Look up UNIHAN character data",
        "description": SEARCH_DESCRIPTION,
    }
    if formatter_class is not None:
        parser_kwargs["formatter_class"] = formatter_class

    parser = subparsers.add_parser("search", **parser_kwargs)

    parser.add_argument(
        "char",
        help="Character, UCN (U+XXXX), or hex codepoint to look up.",
    )
    parser.add_argument(
        "-f",
        "--fields",
        dest="fields",
        nargs="*",
        help="Fields to include in output. Shows all non-empty fields by default.",
    )

    add_output_arguments(parser)

    return parser


def normalize_char_input(char_input: str) -> str:
    """Normalize character input to a single character.

    Accepts:
    - A single character (e.g., "一")
    - UCN format (e.g., "U+4E00")
    - Hex codepoint (e.g., "4E00")

    Parameters
    ----------
    char_input : str
        Character, UCN, or hex codepoint.

    Returns
    -------
    str
        Normalized single character.

    Raises
    ------
    ValueError
        If input cannot be converted to a character.
    """
    char_input = char_input.strip()

    # If it's already a single character, return it
    if len(char_input) == 1:
        return char_input

    # Check if it's a UCN or hex codepoint
    ucn_pattern = re.compile(r"^U?\+?([0-9A-Fa-f]{4,6})$")
    match = ucn_pattern.match(char_input)
    if match:
        hex_code = match.group(1)
        return ucn_to_unicode(hex_code)

    # Try to parse as hex directly
    try:
        code_point = int(char_input, 16)
        return chr(code_point)
    except ValueError:
        pass

    msg = f"Cannot parse character input: {char_input!r}"
    raise ValueError(msg)


def char_to_ucn(char: str) -> str:
    """Convert a character to UCN format.

    Parameters
    ----------
    char : str
        Single character.

    Returns
    -------
    str
        UCN format string (e.g., "U+4E00").
    """
    return f"U+{ord(char):04X}"


def command_search(
    args: Namespace,
    parser: ArgumentParser,
) -> int:
    """Execute the search command.

    Parameters
    ----------
    args : Namespace
        Parsed command-line arguments.
    parser : ArgumentParser
        The argument parser (for error handling).

    Returns
    -------
    int
        Exit code (0 for success, non-zero for failure).
    """
    char_input = args.char
    fields_filter = getattr(args, "fields", None)
    output_format = get_output_format_from_args(args)

    # Normalize character input
    try:
        char = normalize_char_input(char_input)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    ucn = char_to_ucn(char)

    try:
        # Load UNIHAN data using Packager
        # Use python format to get data in memory
        packager = Packager(Options(format="python"))
        packager.download()
        data = packager.export()

        if data is None:
            print("Error: Failed to load UNIHAN data", file=sys.stderr)
            return 1

        # Find the character in the data
        char_data = None
        for record in data:
            if record.get("char") == char or record.get("ucn") == ucn:
                char_data = record
                break

        if char_data is None:
            print(f"Character not found: {char} ({ucn})", file=sys.stderr)
            return 1

        # Filter fields if specified
        if fields_filter:
            filtered_data: dict[str, t.Any] = {
                "char": char_data.get("char"),
                "ucn": char_data.get("ucn"),
            }
            for field in fields_filter:
                if field in char_data:
                    filtered_data[field] = char_data[field]
            char_data = filtered_data
        else:
            # Remove empty fields for cleaner output
            char_data = {k: v for k, v in char_data.items() if v is not None}

    except Exception as e:
        log.exception("Search failed")
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Output the result
    if output_format == OutputFormat.TABLE:
        # For table output, format as key-value pairs
        print(f"Character: {char_data.get('char', 'N/A')}")
        print(f"UCN: {char_data.get('ucn', 'N/A')}")
        print("-" * 40)
        for key, value in char_data.items():
            if key not in ("char", "ucn"):
                # Format complex values
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value[:5])
                    if len(char_data.get(key, [])) > 5:
                        value += "..."
                elif isinstance(value, dict):
                    value = str(value)
                print(f"{key}: {value}")
    else:
        # For JSON/NDJSON, output as-is
        print_output(char_data, output_format)

    return 0


__all__ = [
    "SEARCH_DESCRIPTION",
    "char_to_ucn",
    "command_search",
    "create_search_subparser",
    "normalize_char_input",
]
