"""Export subcommand for unihan-etl CLI.

This module provides the export subcommand that downloads UNIHAN data
and exports it to CSV, JSON, or YAML format.
"""

from __future__ import annotations

import logging
import sys
import typing as t

from unihan_etl.cli._colors import build_description
from unihan_etl.constants import (
    ALLOWED_EXPORT_TYPES,
    DESTINATION_DIR,
    UNIHAN_FIELDS,
    UNIHAN_FILES,
    UNIHAN_URL,
    UNIHAN_ZIP_PATH,
    WORK_DIR,
)
from unihan_etl.core import DEFAULT_OPTIONS, Packager
from unihan_etl.options import Options

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction

log = logging.getLogger(__name__)


EXPORT_DESCRIPTION = build_description(
    """Export UNIHAN data to CSV, JSON, or YAML.

Download, process, and export Unicode Han character database.""",
    (
        (
            None,
            [
                "unihan-etl export",
                "unihan-etl export -F json",
                "unihan-etl export -F json -f kDefinition kMandarin",
                "unihan-etl export -d /tmp/unihan.csv",
            ],
        ),
        (
            "Format examples",
            [
                "unihan-etl export -F csv",
                "unihan-etl export -F json --no-expand",
                "unihan-etl export -F yaml --no-prune",
            ],
        ),
    ),
)


def create_export_subparser(
    subparsers: _SubParsersAction[ArgumentParser],
    formatter_class: type[t.Any] | None = None,
) -> ArgumentParser:
    """Create and configure the export subcommand parser.

    Parameters
    ----------
    subparsers : _SubParsersAction
        Subparser action from parent parser.
    formatter_class : type | None
        Optional formatter class for help output.

    Returns
    -------
    ArgumentParser
        Configured export subcommand parser.
    """
    parser_kwargs: dict[str, t.Any] = {
        "help": "Export UNIHAN data to CSV, JSON, or YAML",
        "description": EXPORT_DESCRIPTION,
    }
    if formatter_class is not None:
        parser_kwargs["formatter_class"] = formatter_class

    parser = subparsers.add_parser("export", **parser_kwargs)

    parser.add_argument(
        "-s",
        "--source",
        dest="source",
        help=f"URL or path of zipfile. Default: {UNIHAN_URL}",
    )
    parser.add_argument(
        "-z",
        "--zip-path",
        dest="zip_path",
        help=f"Path the zipfile is downloaded to. Default: {UNIHAN_ZIP_PATH}",
    )
    parser.add_argument(
        "-d",
        "--destination",
        dest="destination",
        help=f"Output file. Default: {DESTINATION_DIR}/unihan.{{json,csv,yaml}}",
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help=f"Working directory for extraction. Default: {WORK_DIR}",
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="format",
        choices=ALLOWED_EXPORT_TYPES,
        help=f"Output format. Default: {DEFAULT_OPTIONS.format}",
    )
    parser.add_argument(
        "--no-expand",
        dest="expand",
        action="store_false",
        help=(
            "Don't expand values to lists in multi-value UNIHAN fields. "
            "Doesn't apply to CSVs."
        ),
    )
    parser.add_argument(
        "--no-prune",
        dest="prune_empty",
        action="store_false",
        help="Don't prune fields with empty keys. Doesn't apply to CSVs.",
    )
    parser.add_argument(
        "--no-cache",
        dest="cache",
        action="store_false",
        help="Don't cache the UNIHAN zip file or CSV outputs.",
    )
    parser.add_argument(
        "-f",
        "--fields",
        dest="fields",
        nargs="*",
        help=(
            "Fields to use in export. Separated by spaces. "
            f"All fields used by default. Fields: {', '.join(UNIHAN_FIELDS)}"
        ),
    )
    parser.add_argument(
        "-i",
        "--input-files",
        dest="input_files",
        nargs="*",
        help=(
            "Files inside zip to pull data from. Separated by spaces. "
            f"All files used by default. Files: {', '.join(UNIHAN_FILES)}"
        ),
    )

    return parser


def command_export(
    args: Namespace,
    parser: ArgumentParser,
) -> int:
    """Execute the export command.

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
    try:
        # Build options from arguments, filtering out None values and empty lists
        # (empty lists from nargs='*' args like --fields without values)
        option_kwargs = {
            k: v
            for k, v in vars(args).items()
            if v is not None and v != [] and k not in ("subparser_name", "log_level")
        }

        packager = Packager(Options(**option_kwargs))
        packager.download()
        packager.export()
    except Exception as e:
        log.exception("Export failed")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    else:
        return 0


__all__ = [
    "EXPORT_DESCRIPTION",
    "command_export",
    "create_export_subparser",
]
