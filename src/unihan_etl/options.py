"""Configuration for the unihan-etl package."""

from __future__ import annotations

import dataclasses
import pathlib
import typing as t

from .constants import (
    DESTINATION_DIR,
    INDEX_FIELDS,
    UNIHAN_FIELDS,
    UNIHAN_FILES,
    UNIHAN_URL,
    UNIHAN_ZIP_PATH,
    WORK_DIR,
)

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from .types import LogLevel


@dataclasses.dataclass()
class Options:
    """Options for unihan-etl.

    Attributes
    ----------
    source : str | pathlib.Path
        URL or local path of the UNIHAN zip to read.
    destination : pathlib.Path
        Export path. An ``{ext}`` placeholder in it is filled with ``format``.
    zip_path : pathlib.Path
        Path the zip is downloaded to and read back from.
    work_dir : pathlib.Path
        Directory the zip's data files are extracted into.
    fields : Sequence[str]
        UNIHAN fields to export, index fields included.
    format : t.Literal["json", "csv", "yaml", "python"]
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

    source: str | pathlib.Path = UNIHAN_URL
    destination: pathlib.Path = DESTINATION_DIR / "unihan.{ext}"
    zip_path: pathlib.Path = UNIHAN_ZIP_PATH
    work_dir: pathlib.Path = WORK_DIR
    fields: Sequence[str] = dataclasses.field(
        default_factory=lambda: INDEX_FIELDS + UNIHAN_FIELDS,
    )
    format: t.Literal["json", "csv", "yaml", "python"] = "csv"
    input_files: list[str] = dataclasses.field(default_factory=lambda: UNIHAN_FILES)
    download: bool = False
    expand: bool = True
    prune_empty: bool = True
    cache: bool = True
    log_level: LogLevel = "INFO"

    def __post_init__(self) -> None:
        """Post-initialization for unihan-etl options."""
        self.destination = pathlib.Path(str(self.destination).format(ext=self.format))
