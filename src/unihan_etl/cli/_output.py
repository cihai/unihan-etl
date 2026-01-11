r"""Output formatting utilities for unihan-etl CLI.

This module provides consistent output formatting for CLI commands
supporting JSON, NDJSON, and table output formats.

Examples
--------
>>> from unihan_etl.cli._output import OutputFormat, format_output

Format data as JSON:

>>> data = [{"name": "kDefinition", "file": "Unihan_Readings.txt"}]
>>> result = format_output(data, OutputFormat.JSON)
>>> '"name":' in result
True

Format data as NDJSON (newline-delimited JSON):

>>> result = format_output(data, OutputFormat.NDJSON)
>>> result.endswith("\n")
True
"""

from __future__ import annotations

import enum
import json
import sys
import typing as t

if t.TYPE_CHECKING:
    from argparse import ArgumentParser
    from typing import TextIO


class OutputFormat(enum.Enum):
    """Output format options for CLI commands.

    Examples
    --------
    >>> OutputFormat.TABLE.value
    'table'
    >>> OutputFormat.JSON.value
    'json'
    >>> OutputFormat.NDJSON.value
    'ndjson'
    """

    TABLE = "table"
    JSON = "json"
    NDJSON = "ndjson"


def format_table(
    data: list[dict[str, t.Any]],
    headers: list[str] | None = None,
    column_widths: dict[str, int] | None = None,
) -> str:
    """Format data as a simple text table.

    Parameters
    ----------
    data : list[dict[str, Any]]
        List of dictionaries to format as table rows.
    headers : list[str] | None
        Column headers to display. If None, uses keys from first row.
    column_widths : dict[str, int] | None
        Minimum column widths by header name. If None, auto-calculated.

    Returns
    -------
    str
        Formatted table string.

    Examples
    --------
    >>> data = [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}]
    >>> result = format_table(data)
    >>> "name" in result
    True
    >>> "a" in result
    True
    """
    if not data:
        return ""

    # Determine headers from first row if not provided
    if headers is None:
        headers = list(data[0].keys())

    # Calculate column widths
    widths: dict[str, int] = {}
    for header in headers:
        max_width = len(header)
        for row in data:
            value = str(row.get(header, ""))
            max_width = max(max_width, len(value))
        # Apply minimum width if specified
        if column_widths and header in column_widths:
            max_width = max(max_width, column_widths[header])
        widths[header] = max_width

    # Build header line
    header_parts = [header.ljust(widths[header]) for header in headers]
    header_line = "  ".join(header_parts)

    # Build separator line
    separator_parts = ["-" * widths[header] for header in headers]
    separator_line = "  ".join(separator_parts)

    # Build data rows
    rows = []
    for row in data:
        row_parts = [
            str(row.get(header, "")).ljust(widths[header]) for header in headers
        ]
        rows.append("  ".join(row_parts))

    return "\n".join([header_line, separator_line, *rows])


def format_json(data: list[dict[str, t.Any]] | dict[str, t.Any]) -> str:
    """Format data as pretty-printed JSON.

    Parameters
    ----------
    data : list[dict[str, Any]] | dict[str, Any]
        Data to format as JSON.

    Returns
    -------
    str
        Pretty-printed JSON string.

    Examples
    --------
    >>> data = [{"name": "kDefinition"}]
    >>> result = format_json(data)
    >>> '"name"' in result
    True
    >>> result.startswith("[")
    True
    """
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_ndjson(data: list[dict[str, t.Any]]) -> str:
    r"""Format data as newline-delimited JSON (NDJSON).

    Each record is serialized as a single-line JSON object,
    with one record per line. This format is ideal for:
    - Streaming processing
    - Unix pipe composability
    - LLM consumption

    Parameters
    ----------
    data : list[dict[str, Any]]
        List of records to format.

    Returns
    -------
    str
        NDJSON string with one record per line.

    Examples
    --------
    >>> data = [{"name": "a"}, {"name": "b"}]
    >>> result = format_ndjson(data)
    >>> result.count("\n")
    2
    >>> '{"name": "a"}' in result
    True
    """
    lines = [json.dumps(record, ensure_ascii=False) for record in data]
    return "\n".join(lines) + "\n" if lines else ""


def format_output(
    data: list[dict[str, t.Any]] | dict[str, t.Any],
    output_format: OutputFormat,
    headers: list[str] | None = None,
) -> str:
    r"""Format data for output in specified format.

    Parameters
    ----------
    data : list[dict[str, Any]] | dict[str, Any]
        Data to format. For TABLE format, must be a list.
    output_format : OutputFormat
        Desired output format.
    headers : list[str] | None
        Column headers for TABLE format. If None, uses keys from first row.

    Returns
    -------
    str
        Formatted output string.

    Raises
    ------
    ValueError
        If TABLE format is requested for non-list data.

    Examples
    --------
    >>> data = [{"name": "kDefinition", "file": "Unihan_Readings.txt"}]

    >>> result = format_output(data, OutputFormat.JSON)
    >>> '"name":' in result
    True

    >>> result = format_output(data, OutputFormat.NDJSON)
    >>> result.endswith("\n")
    True

    >>> result = format_output(data, OutputFormat.TABLE)
    >>> "name" in result
    True
    """
    if output_format == OutputFormat.JSON:
        return format_json(data)
    if output_format == OutputFormat.NDJSON:
        if not isinstance(data, list):
            data = [data]
        return format_ndjson(data)
    if output_format == OutputFormat.TABLE:
        if not isinstance(data, list):
            msg = "TABLE format requires list data"
            raise ValueError(msg)
        return format_table(data, headers=headers)
    # Fallback (should not reach here with Enum)
    return str(data)


def print_output(
    data: list[dict[str, t.Any]] | dict[str, t.Any],
    output_format: OutputFormat,
    headers: list[str] | None = None,
    file: TextIO | None = None,
) -> None:
    """Print formatted output to file/stdout.

    Parameters
    ----------
    data : list[dict[str, Any]] | dict[str, Any]
        Data to format and print.
    output_format : OutputFormat
        Desired output format.
    headers : list[str] | None
        Column headers for TABLE format.
    file : TextIO | None
        Output file. Default is sys.stdout.

    Examples
    --------
    >>> import io
    >>> data = [{"name": "test"}]
    >>> buf = io.StringIO()
    >>> print_output(data, OutputFormat.JSON, file=buf)
    >>> '"name"' in buf.getvalue()
    True
    """
    if file is None:
        file = sys.stdout
    output = format_output(data, output_format, headers=headers)
    print(output, file=file)


def get_output_format_from_args(args: t.Any) -> OutputFormat:
    """Determine output format from parsed arguments.

    Checks for --json and --ndjson flags on args namespace.
    Defaults to TABLE if neither is set.

    Parameters
    ----------
    args : Any
        Parsed argparse namespace with json and ndjson attributes.

    Returns
    -------
    OutputFormat
        The determined output format.

    Examples
    --------
    >>> from argparse import Namespace
    >>> args = Namespace(json=True, ndjson=False)
    >>> get_output_format_from_args(args)
    <OutputFormat.JSON: 'json'>

    >>> args = Namespace(json=False, ndjson=True)
    >>> get_output_format_from_args(args)
    <OutputFormat.NDJSON: 'ndjson'>

    >>> args = Namespace(json=False, ndjson=False)
    >>> get_output_format_from_args(args)
    <OutputFormat.TABLE: 'table'>
    """
    if getattr(args, "json", False):
        return OutputFormat.JSON
    if getattr(args, "ndjson", False):
        return OutputFormat.NDJSON
    return OutputFormat.TABLE


def add_output_arguments(parser: ArgumentParser) -> None:
    """Add --json and --ndjson arguments to a parser.

    Parameters
    ----------
    parser : ArgumentParser
        Parser to add arguments to.

    Examples
    --------
    >>> import argparse
    >>> parser = argparse.ArgumentParser()
    >>> add_output_arguments(parser)
    >>> args = parser.parse_args(["--json"])
    >>> args.json
    True
    >>> args = parser.parse_args(["--ndjson"])
    >>> args.ndjson
    True
    """
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    output_group.add_argument(
        "--ndjson",
        action="store_true",
        default=False,
        help="Output as newline-delimited JSON (one record per line)",
    )


__all__ = [
    "OutputFormat",
    "add_output_arguments",
    "format_json",
    "format_ndjson",
    "format_output",
    "format_table",
    "get_output_format_from_args",
    "print_output",
]
