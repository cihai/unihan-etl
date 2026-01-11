"""Fields subcommand for unihan-etl CLI.

This module provides the fields subcommand that lists available
UNIHAN fields with their source files.
"""

from __future__ import annotations

import typing as t

from unihan_etl.cli._colors import build_description
from unihan_etl.cli._output import (
    OutputFormat,
    add_output_arguments,
    get_output_format_from_args,
    print_output,
)
from unihan_etl.constants import UNIHAN_MANIFEST

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction


FIELDS_DESCRIPTION = build_description(
    """List available UNIHAN fields.

Show all fields that can be exported from the UNIHAN database,
along with which source file contains each field.""",
    (
        (
            None,
            [
                "unihan-etl fields",
                "unihan-etl fields --json",
                "unihan-etl fields --ndjson",
                "unihan-etl fields -i Unihan_Readings.txt",
            ],
        ),
    ),
)


def create_fields_subparser(
    subparsers: _SubParsersAction[ArgumentParser],
    formatter_class: type[t.Any] | None = None,
) -> ArgumentParser:
    """Create and configure the fields subcommand parser.

    Parameters
    ----------
    subparsers : _SubParsersAction
        Subparser action from parent parser.
    formatter_class : type | None
        Optional formatter class for help output.

    Returns
    -------
    ArgumentParser
        Configured fields subcommand parser.
    """
    parser_kwargs: dict[str, t.Any] = {
        "help": "List available UNIHAN fields",
        "description": FIELDS_DESCRIPTION,
    }
    if formatter_class is not None:
        parser_kwargs["formatter_class"] = formatter_class

    parser = subparsers.add_parser("fields", **parser_kwargs)

    parser.add_argument(
        "-i",
        "--input-files",
        dest="input_files",
        nargs="*",
        help="Filter fields by source file(s). Shows all fields by default.",
    )

    add_output_arguments(parser)

    return parser


def get_fields_data(input_files: list[str] | None = None) -> list[dict[str, str]]:
    """Get field data from UNIHAN manifest.

    Parameters
    ----------
    input_files : list[str] | None
        Optional list of files to filter by. If None, returns all fields.

    Returns
    -------
    list[dict[str, str]]
        List of field records with 'name' and 'file' keys.
    """
    fields_data: list[dict[str, str]] = []

    for file_name, fields in UNIHAN_MANIFEST.items():
        # Filter by input files if specified
        if input_files is not None and file_name not in input_files:
            continue

        fields_data.extend({"name": field, "file": file_name} for field in fields)

    # Sort by field name
    fields_data.sort(key=lambda x: x["name"])

    return fields_data


def command_fields(
    args: Namespace,
    parser: ArgumentParser,
) -> int:
    """Execute the fields command.

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
    input_files = getattr(args, "input_files", None)
    output_format = get_output_format_from_args(args)

    fields_data = get_fields_data(input_files)

    if not fields_data:
        if input_files:
            print(f"No fields found in files: {', '.join(input_files)}")
        else:
            print("No fields found")
        return 1

    print_output(fields_data, output_format, headers=["name", "file"])

    # Print count in table mode
    if output_format == OutputFormat.TABLE:
        print(f"\nTotal: {len(fields_data)} fields")

    return 0


__all__ = [
    "FIELDS_DESCRIPTION",
    "command_fields",
    "create_fields_subparser",
    "get_fields_data",
]
