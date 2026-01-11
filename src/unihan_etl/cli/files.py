"""Files subcommand for unihan-etl CLI.

This module provides the files subcommand that lists available
UNIHAN source files with their field counts.
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


FILES_DESCRIPTION = build_description(
    """List available UNIHAN source files.

Show all UNIHAN source files that can be used for data extraction,
along with their field counts.""",
    (
        (
            None,
            [
                "unihan-etl files",
                "unihan-etl files --json",
                "unihan-etl files --ndjson",
                "unihan-etl files --with-fields",
            ],
        ),
    ),
)


def create_files_subparser(
    subparsers: _SubParsersAction[ArgumentParser],
    formatter_class: type[t.Any] | None = None,
) -> ArgumentParser:
    """Create and configure the files subcommand parser.

    Parameters
    ----------
    subparsers : _SubParsersAction
        Subparser action from parent parser.
    formatter_class : type | None
        Optional formatter class for help output.

    Returns
    -------
    ArgumentParser
        Configured files subcommand parser.
    """
    parser_kwargs: dict[str, t.Any] = {
        "help": "List available UNIHAN source files",
        "description": FILES_DESCRIPTION,
    }
    if formatter_class is not None:
        parser_kwargs["formatter_class"] = formatter_class

    parser = subparsers.add_parser("files", **parser_kwargs)

    parser.add_argument(
        "--with-fields",
        dest="with_fields",
        action="store_true",
        help="Include list of fields for each file.",
    )

    add_output_arguments(parser)

    return parser


def get_files_data(with_fields: bool = False) -> list[dict[str, t.Any]]:
    """Get file data from UNIHAN manifest.

    Parameters
    ----------
    with_fields : bool
        If True, include field list for each file.

    Returns
    -------
    list[dict[str, Any]]
        List of file records with 'name', 'field_count', and optionally 'fields'.
    """
    files_data: list[dict[str, t.Any]] = []

    for file_name, fields in UNIHAN_MANIFEST.items():
        record: dict[str, t.Any] = {
            "name": file_name,
            "field_count": len(fields),
        }
        if with_fields:
            record["fields"] = list(fields)
        files_data.append(record)

    # Sort by file name
    files_data.sort(key=lambda x: x["name"])

    return files_data


def command_files(
    args: Namespace,
    parser: ArgumentParser,
) -> int:
    """Execute the files command.

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
    with_fields = getattr(args, "with_fields", False)
    output_format = get_output_format_from_args(args)

    files_data = get_files_data(with_fields)

    if not files_data:
        print("No files found")
        return 1

    # For table output, show fields as comma-separated if requested
    if output_format == OutputFormat.TABLE and with_fields:
        for record in files_data:
            record["fields"] = ", ".join(record["fields"][:3]) + (
                "..." if len(record.get("fields", [])) > 3 else ""
            )

    headers = ["name", "field_count"]
    if with_fields:
        headers.append("fields")

    print_output(files_data, output_format, headers=headers)

    # Print count in table mode
    if output_format == OutputFormat.TABLE:
        total_fields = sum(f["field_count"] for f in files_data)
        print(f"\nTotal: {len(files_data)} files, {total_fields} fields")

    return 0


__all__ = [
    "FILES_DESCRIPTION",
    "command_files",
    "create_files_subparser",
    "get_files_data",
]
