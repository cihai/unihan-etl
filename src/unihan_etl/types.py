"""Typings for unihan-etl."""

import dataclasses
import pathlib
import sys
import typing as t

if t.TYPE_CHECKING:
    from http.client import HTTPMessage
    from os import PathLike
    from urllib.request import _DataType

    from typing_extensions import TypeAlias

StrPath: "TypeAlias" = t.Union[str, "PathLike[str]"]
""":class:`os.PathLike` or :class:`str`

:class:`StrPath` is based on `typeshed`__'s.

.. __: https://github.com/python/typeshed/blob/5df8de7/stdlib/_typeshed/__init__.pyi#L115-L118
"""  # E501

# Log levels
LogLevel = t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Column data
ColumnData = t.Sequence[str]
ColumnDataTuple = t.Tuple[str, ...]

# In situ
UntypedUnihanData = t.Mapping[str, t.Any]

UntypedNormalizedData = t.Sequence[UntypedUnihanData]

# Export w/ listify()
ListifiedExport = t.List[t.List[str]]

# Export w/ listify() -> expand_delimiters()
ExpandedExport = t.Sequence[t.Mapping[str, t.Any]]

# Valid output formats
UnihanFormats = t.Literal["json", "csv", "yaml", "python"]


@dataclasses.dataclass()
class Options:
    """unihan-etl options."""

    source: str
    destination: pathlib.Path
    zip_path: pathlib.Path
    work_dir: pathlib.Path
    fields: t.Tuple[str, ...]
    format: UnihanFormats
    input_files: t.List[str]
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
        filename: t.Optional["StrPath"] = None,
        reporthook: t.Optional["ReportHookFn"] = None,
        data: "t.Optional[_DataType]" = None,
    ) -> t.Tuple[str, "HTTPMessage"]:
        """Download logic for :func:`urllib.request.urlretrieve`."""
        ...
