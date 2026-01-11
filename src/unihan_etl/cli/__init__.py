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
from unihan_etl.cli._colors import ColorMode, Colors, build_description, get_color_mode
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
            "Download",  # Colorized as category inside examples block
            [
                "unihan-etl download",
            ],
        ),
        (
            "Explore",  # Colorized as category inside examples block
            [
                "unihan-etl fields",
                "unihan-etl files",
                "unihan-etl search 好",
            ],
        ),
    ),
)


def create_parser(colors: Colors | None = None) -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands.

    Parameters
    ----------
    colors : Colors | None
        Colors instance for styling. If None, uses ColorMode.AUTO.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser with all subcommands.
    """
    if colors is None:
        colors = Colors(ColorMode.AUTO)

    formatter_class = create_themed_formatter(colors)

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
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Color output mode. Default: auto",
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

    # First pass to get color mode (before full parse)
    # This allows help text to be colored correctly
    color_mode = ColorMode.AUTO
    for i, arg in enumerate(args):
        if arg == "--color" and i + 1 < len(args):
            color_mode = get_color_mode(args[i + 1])
            break
        if arg.startswith("--color="):
            color_mode = get_color_mode(arg.split("=", 1)[1])
            break

    colors = Colors(color_mode)
    parser = create_parser(colors)
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
