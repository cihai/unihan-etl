import pathlib
import typing as t
from os import PathLike
import sys

if t.TYPE_CHECKING:
    from typing_extensions import TypeAlias
    from urllib.request import _DataType
    from http.client import HTTPMessage

StrPath: "TypeAlias" = t.Union[str, "PathLike[str]"]  # stable
""":class:`os.PathLike` or :class:`str`

:class:`StrPath` is based on `typeshed's`_.

.. _typeshed's: https://github.com/python/typeshed/blob/5df8de7/stdlib/_typeshed/__init__.pyi#L115-L118
"""  # NOQA E501

# Column data
ColumnData = t.Sequence[str]
ColumnDataTuple = t.Tuple[str, ...]

# In situ
UntypedUnihanData = t.Mapping[str, t.Any]

# Export (standard)
UntypedNormalizedData = t.Sequence[UntypedUnihanData]

# Export w/ listify()
ListifiedExport = t.List[t.List[str]]

# Export w/ listify() -> expand_delimiters()
ExpandedExport = t.Sequence[t.Mapping[str, t.Any]]


class OptionsDict(t.TypedDict):
    source: str
    destination: pathlib.Path
    zip_path: pathlib.Path
    work_dir: pathlib.Path
    fields: t.Tuple[str, ...]
    format: t.Literal["json", "csv", "yaml", "python"]
    input_files: t.List[str]
    download: bool
    expand: bool
    prune_empty: bool
    cache: bool
    log_level: t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ReportHookFn(t.Protocol):
    def __call__(
        self, count: int, block_size: int, total_size: int, out: t.IO[str] = sys.stdout
    ) -> object:
        ...


class UrlRetrieveFn(t.Protocol):
    def __call__(
        self,
        url: str,
        filename: t.Optional["StrPath"] = None,
        reporthook: t.Optional["ReportHookFn"] = None,
        data: "_DataType" = None,
    ) -> t.Tuple[str, "HTTPMessage"]:
        ...
