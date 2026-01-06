"""Typings for unihan-etl."""

from __future__ import annotations

import contextlib
import dataclasses
import pathlib
import sys
import typing as t
import zipfile
from collections.abc import Generator, Mapping, Sequence

if t.TYPE_CHECKING:
    from http.client import HTTPMessage
    from os import PathLike
    from typing import TypeAlias
    from urllib.request import _DataType

    from unihan_etl.core import Packager

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


# ---------------------------------------------------------------------------
# Pytest fixture types
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class UnihanZip:
    """Container for UNIHAN zip file with lazy access.

    Provides safe access to zip file contents without leaving handles open.
    Use the :meth:`open` context manager when you need to work with the
    zip file directly.

    Examples
    --------
    >>> zip_container = UnihanZip(pathlib.Path("/path/to/Unihan.zip"))
    >>> zip_container.path
    PosixPath('/path/to/Unihan.zip')
    >>> with zip_container.open() as zf:
    ...     print(zf.namelist())  # doctest: +SKIP
    ['Unihan_Readings.txt', ...]
    """

    path: pathlib.Path

    @contextlib.contextmanager
    def open(
        self,
        mode: t.Literal["r", "w", "a", "x"] = "r",
    ) -> Generator[zipfile.ZipFile, None, None]:
        """Open the zip file as a context manager.

        Parameters
        ----------
        mode : Literal["r", "w", "a", "x"], optional
            Mode to open the zip file, by default 'r'

        Yields
        ------
        zipfile.ZipFile
            Open zip file handle
        """
        with zipfile.ZipFile(self.path, mode) as zf:
            yield zf

    @property
    def namelist(self) -> list[str]:
        """Get list of files in the zip archive.

        Returns
        -------
        list[str]
            Names of files in the archive
        """
        with self.open() as zf:
            return zf.namelist()

    def extract(self, dest: pathlib.Path) -> None:
        """Extract all files to destination directory.

        Parameters
        ----------
        dest : pathlib.Path
            Directory to extract files to
        """
        with self.open() as zf:
            zf.extractall(dest)

    def exists(self) -> bool:
        """Check if the zip file exists.

        Returns
        -------
        bool
            True if the zip file exists on disk
        """
        return self.path.exists()


@dataclasses.dataclass(frozen=True)
class UnihanDataset:
    """Complete UNIHAN dataset container with paths and metadata.

    This is the primary fixture type for working with UNIHAN test data.
    It provides access to all paths and lazy data loading.

    Attributes
    ----------
    name : Literal["quick", "full"]
        Dataset type identifier
    root : pathlib.Path
        Root directory for this dataset
    zip : UnihanZip
        Zip file container with lazy access methods
    work_dir : pathlib.Path
        Working directory for extracted files
    destination : pathlib.Path
        Path to exported CSV/JSON/YAML output

    Examples
    --------
    >>> dataset = UnihanDataset(
    ...     name="quick",
    ...     root=pathlib.Path("/cache/quick"),
    ...     zip=UnihanZip(pathlib.Path("/cache/quick/Unihan.zip")),
    ...     work_dir=pathlib.Path("/cache/quick/work"),
    ...     destination=pathlib.Path("/cache/quick/out/unihan.csv"),
    ... )
    >>> dataset.is_ready
    False
    """

    name: t.Literal["quick", "full"]
    root: pathlib.Path
    zip: UnihanZip
    work_dir: pathlib.Path
    destination: pathlib.Path

    @property
    def is_ready(self) -> bool:
        """Check if dataset has been extracted and exported.

        Returns
        -------
        bool
            True if destination file exists
        """
        return self.destination.exists()

    @property
    def zip_path(self) -> pathlib.Path:
        """Convenience accessor for zip file path.

        Returns
        -------
        pathlib.Path
            Path to the zip file
        """
        return self.zip.path


@dataclasses.dataclass
class UnihanData:
    """Lazy-loaded UNIHAN data container.

    Provides deferred loading of normalized and expanded UNIHAN data.
    Data is only loaded when the corresponding property is accessed.

    Attributes
    ----------
    packager : Packager
        The packager instance to load data from

    Examples
    --------
    >>> # Data isn't loaded until accessed:
    >>> data = UnihanData(packager)  # doctest: +SKIP
    >>> data.normalized  # Loads normalized data  # doctest: +SKIP
    >>> data.expanded    # Loads expanded data  # doctest: +SKIP
    """

    packager: Packager
    _normalized: UntypedNormalizedData | None = dataclasses.field(
        default=None,
        repr=False,
    )
    _expanded: ExpandedExport | None = dataclasses.field(
        default=None,
        repr=False,
    )
    _by_char: dict[str, UntypedUnihanData] | None = dataclasses.field(
        default=None,
        repr=False,
    )

    def _load_normalized(self) -> UntypedNormalizedData:
        """Load normalized data from packager."""
        from unihan_etl import core

        files = [
            self.packager.options.work_dir / f
            for f in self.packager.options.input_files
            if (self.packager.options.work_dir / f).exists()
        ]
        data = core.load_data(files=files)
        return core.normalize(data, list(self.packager.options.fields))

    @property
    def normalized(self) -> UntypedNormalizedData:
        """Get normalized UNIHAN data (lazy-loaded).

        Returns
        -------
        UntypedNormalizedData
            Sequence of normalized UNIHAN records
        """
        if self._normalized is None:
            self._normalized = self._load_normalized()
        return self._normalized

    @property
    def expanded(self) -> ExpandedExport:
        """Get expanded UNIHAN data (lazy-loaded).

        Expands delimited fields into structured lists/dicts.

        Returns
        -------
        ExpandedExport
            Sequence of expanded UNIHAN records
        """
        if self._expanded is None:
            from unihan_etl.core import expand_delimiters

            self._expanded = expand_delimiters(list(self.normalized))
        return self._expanded

    @property
    def by_char(self) -> dict[str, UntypedUnihanData]:
        """Get data indexed by character for fast lookup.

        Returns
        -------
        dict[str, UntypedUnihanData]
            Dictionary mapping characters to their data
        """
        if self._by_char is None:
            self._by_char = {item["char"]: item for item in self.expanded}
        return self._by_char


# ---------------------------------------------------------------------------
# Protocol types
# ---------------------------------------------------------------------------


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
