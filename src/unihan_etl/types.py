import pathlib
import typing as t
from os import PathLike

if t.TYPE_CHECKING:
    from typing_extensions import TypeAlias

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
    format: str
    input_files: t.List[str]
    download: bool
    expand: bool
    prune_empty: bool
    cache: bool
    log_level: t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


ReportHookFn = t.Callable[[int, int, int], object]
