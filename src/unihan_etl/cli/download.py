"""Download subcommand for unihan-etl CLI.

This module provides the download subcommand that downloads and caches
the UNIHAN database without exporting.
"""

from __future__ import annotations

import logging
import sys
import typing as t

from unihan_etl._internal.private_path import PrivatePath
from unihan_etl.cli._colors import build_description
from unihan_etl.constants import (
    UNIHAN_URL,
    UNIHAN_ZIP_PATH,
    WORK_DIR,
)
from unihan_etl.core import Packager
from unihan_etl.options import Options

if t.TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace, _SubParsersAction

log = logging.getLogger(__name__)


DOWNLOAD_DESCRIPTION = build_description(
    """Download and cache UNIHAN database.

Download the Unicode Han database without processing or exporting.
Use this to pre-cache the data for later export commands.""",
    (
        (
            None,
            [
                "unihan-etl download",
                "unihan-etl download --no-cache",
                "unihan-etl download -z /tmp/Unihan.zip",
            ],
        ),
    ),
)


def create_download_subparser(
    subparsers: _SubParsersAction[ArgumentParser],
    formatter_class: type[t.Any] | None = None,
) -> ArgumentParser:
    """Create and configure the download subcommand parser.

    Parameters
    ----------
    subparsers : _SubParsersAction
        Subparser action from parent parser.
    formatter_class : type | None
        Optional formatter class for help output.

    Returns
    -------
    ArgumentParser
        Configured download subcommand parser.
    """
    parser_kwargs: dict[str, t.Any] = {
        "help": "Download and cache UNIHAN database",
        "description": DOWNLOAD_DESCRIPTION,
    }
    if formatter_class is not None:
        parser_kwargs["formatter_class"] = formatter_class

    parser = subparsers.add_parser("download", **parser_kwargs)

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
        help=f"Path to download zipfile to. Default: {UNIHAN_ZIP_PATH}",
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help=f"Working directory for extraction. Default: {WORK_DIR}",
    )
    parser.add_argument(
        "--no-cache",
        dest="cache",
        action="store_false",
        help="Force re-download even if cached.",
    )

    return parser


def command_download(
    args: Namespace,
    parser: ArgumentParser,
) -> int:
    """Execute the download command.

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

        # Print success message with privacy-masked path
        zip_path = PrivatePath(packager.options.zip_path)
        work_dir = PrivatePath(packager.options.work_dir)
        print(f"Downloaded to: {zip_path}")
        print(f"Extracted to: {work_dir}")
    except Exception as e:
        log.exception("Download failed")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    else:
        return 0


__all__ = [
    "DOWNLOAD_DESCRIPTION",
    "command_download",
    "create_download_subparser",
]
