"""Typings for unihan-etl."""

from __future__ import annotations

import dataclasses
import sys
import typing as t
from collections.abc import Mapping, Sequence

if t.TYPE_CHECKING:
    import pathlib
    from http.client import HTTPMessage
    from os import PathLike
    from typing import TypeAlias
    from urllib.request import _DataType

StrPath: TypeAlias = t.Union[str, "PathLike[str]"]
""":class:`os.PathLike` or :class:`str`

:class:`StrPath` is based on `typeshed`__'s.

.. __: https://github.com/python/typeshed/blob/5df8de7/stdlib/_typeshed/__init__.pyi#L115-L118
"""  # E501

# Log levels
LogLevel = t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Column data
ColumnData: TypeAlias = Sequence[str]
"""Sequence of UNIHAN field name strings."""

ColumnDataTuple = tuple[str, ...]

# In situ
UntypedUnihanData = Mapping[str, t.Any]

UntypedNormalizedData: TypeAlias = Sequence[UntypedUnihanData]
"""Normalized UNIHAN data as a sequence of field-value mappings."""

# Export w/ listify()
ListifiedExport = list[list[str]]

# Export w/ listify() -> expand_delimiters()
ExpandedExport: TypeAlias = Sequence[Mapping[str, t.Any]]
"""Expanded UNIHAN export with multi-value delimiters resolved."""

# Valid output formats
UnihanFormats = t.Literal["json", "csv", "yaml", "python"]


@dataclasses.dataclass()
class Options:
    """unihan-etl options.

    Attributes
    ----------
    source : str
        URL or path of the UNIHAN zip to read.
    destination : pathlib.Path
        Export path, with any ``{ext}`` placeholder already resolved.
    zip_path : pathlib.Path
        Path the zip is downloaded to and read back from.
    work_dir : pathlib.Path
        Directory the zip's data files are extracted into.
    fields : tuple[str, ...]
        UNIHAN fields to export, index fields included.
    format : UnihanFormats
        Export format.
    input_files : list[str]
        Files inside the zip to pull records from.
    download : bool
        Flag for fetching the zip up front. Downloading happens on demand in
        :meth:`unihan_etl.core.Packager.download`, which does not consult it.
    expand : bool
        Expand multi-value fields into structured values. CSV exports stay
        flat either way.
    prune_empty : bool
        Drop fields with empty values from exported records. Applies only
        alongside ``expand``.
    cache : bool
        Reuse a valid zip and already extracted files rather than downloading
        and extracting again.
    log_level : LogLevel
        Level the logger is set up at.
    """

    source: str
    destination: pathlib.Path
    zip_path: pathlib.Path
    work_dir: pathlib.Path
    fields: tuple[str, ...]
    format: UnihanFormats
    input_files: list[str]
    download: bool
    expand: bool
    prune_empty: bool
    cache: bool
    log_level: LogLevel


class ReportHookFn(t.Protocol):
    """Progress bar callback for download()."""

    def __call__(
        self,
        count: int,
        block_size: int,
        total_size: int,
        out: t.IO[str] = sys.stdout,
    ) -> object:
        """Print progress bar during download."""
        ...


class UrlRetrieveFn(t.Protocol):
    """Type annotation for :func:`urllib.request.urlretrieve`."""

    def __call__(
        self,
        url: str,
        filename: StrPath | None = None,
        reporthook: ReportHookFn | None = None,
        data: _DataType | None = None,
    ) -> tuple[str, HTTPMessage]:
        """Download logic for :func:`urllib.request.urlretrieve`."""
        ...
