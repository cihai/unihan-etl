import typing as t
from collections.abc import Mapping, Sequence

# Column data
ColumnData = Sequence[str]
ColumnDataTuple = t.Tuple[str, ...]

# In situ
UntypedUnihanData = Mapping[str, t.Any]

# Export (standard)
UntypedNormalizedData = t.Sequence[UntypedUnihanData]

# Export w/ listify()
ListifiedExport = t.List[t.List[str]]

# Export w/ listify() -> expand_delimiters()
ExpandedExport = Sequence[Mapping[str, t.Any]]


class OptionsDict(t.TypedDict):
    source: str
    destination: str
    zip_path: str
    work_dir: str
    fields: t.Tuple[str, ...]
    format: str
    input_files: t.List[str]
    download: bool
    expand: bool
    prune_empty: bool
    cache: bool
    log_level: t.Literal["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


ReportHookFn = t.Callable[[int, int, int], object]
