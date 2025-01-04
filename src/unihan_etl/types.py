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
    from urllib.request import _DataType

    from typing_extensions import TypeAlias

StrPath: TypeAlias = t.Union[str, "PathLike[str]"]
""":class:`os.PathLike` or :class:`str`

:class:`StrPath` is based on `typeshed`__'s.

.. __: https://github.com/python/typeshed/blob/5df8de7/stdlib/_typeshed/__init__.pyi#L115-L118
"""  # E501

# Log levels
LogLevel = t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Column data
ColumnData = Sequence[str]
ColumnDataTuple = tuple[str, ...]

# In situ
UntypedUnihanData = Mapping[str, t.Any]

UntypedNormalizedData = Sequence[UntypedUnihanData]

# Export w/ listify()
ListifiedExport = list[list[str]]

# Export w/ listify() -> expand_delimiters()
ExpandedExport = Sequence[Mapping[str, t.Any]]

# Valid output formats
UnihanFormats = t.Literal["json", "csv", "yaml", "python"]


@dataclasses.dataclass()
class Options:
    """unihan-etl options."""

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
