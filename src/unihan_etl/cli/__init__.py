"""Command-line interface for unihan-etl.

This package provides the CLI implementation with subcommands for:
- export: Export UNIHAN data to CSV, JSON, or YAML
- download: Download and cache UNIHAN database
- fields: List available UNIHAN fields
- files: List available UNIHAN source files
- search: Look up character(s) in UNIHAN database
"""

from __future__ import annotations

import argparse
import logging
import sys
import typing as t

from unihan_etl.__about__ import __version__
from unihan_etl.cli._colors import build_description
from unihan_etl.cli._formatter import create_themed_formatter
from unihan_etl.cli.download import command_download, create_download_subparser
from unihan_etl.cli.export import command_export, create_export_subparser
from unihan_etl.cli.fields import command_fields, create_fields_subparser
from unihan_etl.cli.files import command_files, create_files_subparser
from unihan_etl.cli.search import command_search, create_search_subparser
from unihan_etl.core import setup_logger

if t.TYPE_CHECKING:
    from typing import TypeAlias

    from unihan_etl.types import LogLevel

    _ExitCode: TypeAlias = str | int | None


CLI_DESCRIPTION = build_description(
    """unihan-etl - Export UNIHAN data to CSV, JSON, or YAML.

Download and export Unicode Han character database.""",
    (
        (
            None,  # Generates "examples:" to trigger formatter colorization
            [
                "unihan-etl export",
                "unihan-etl export -F json -f kDefinition",
            ],
        ),
        (
            "download",  # Colorized as category inside examples block
            [
                "unihan-etl download",
            ],
        ),
        (
            "explore",  # Colorized as category inside examples block
            [
                "unihan-etl fields",
                "unihan-etl files",
                "unihan-etl search 好",
            ],
        ),
    ),
)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands.

    The formatter uses Python 3.14's native color theming based on TTY
    detection and environment variables (NO_COLOR, FORCE_COLOR).

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser with all subcommands.
    """
    formatter_class = create_themed_formatter()

    parser = argparse.ArgumentParser(
        prog="unihan-etl",
        description=CLI_DESCRIPTION,
        formatter_class=formatter_class,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level. Default: INFO",
    )

    subparsers = parser.add_subparsers(
        dest="subparser_name",
        title="commands",
        description="Available commands (use 'COMMAND --help' for details)",
    )

    # Register subcommands
    create_export_subparser(subparsers, formatter_class)
    create_download_subparser(subparsers, formatter_class)
    create_fields_subparser(subparsers, formatter_class)
    create_files_subparser(subparsers, formatter_class)
    create_search_subparser(subparsers, formatter_class)

    return parser


def cli(args: list[str] | None = None) -> _ExitCode:
    """Run the CLI and dispatch to subcommands.

    Parameters
    ----------
    args : list[str] | None
        Command-line arguments. If None, uses sys.argv[1:].

    Returns
    -------
    int
        Exit code (0 for success, non-zero for failure).
    """
    if args is None:
        args = sys.argv[1:]

    # Python 3.14's argparse handles color detection automatically
    # based on TTY, NO_COLOR, and FORCE_COLOR environment variables
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Setup logging
    log_level = t.cast("LogLevel", getattr(parsed, "log_level", "INFO"))
    setup_logger(logger=None, level=log_level)

    # If no subcommand, show help
    if parsed.subparser_name is None:
        parser.print_help()
        return 0

    # Dispatch to subcommand
    commands: dict[str, t.Callable[[t.Any, argparse.ArgumentParser], int]] = {
        "export": command_export,
        "download": command_download,
        "fields": command_fields,
        "files": command_files,
        "search": command_search,
    }

    command_fn = commands.get(parsed.subparser_name)
    if command_fn is None:
        logging.error("Unknown command: %s", parsed.subparser_name)
        return 1

    return command_fn(parsed, parser)


__all__ = [
    "CLI_DESCRIPTION",
    "cli",
    "create_parser",
]
