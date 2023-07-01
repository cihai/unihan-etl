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
    from .types import LogLevel


@dataclasses.dataclass()
class Options:
    source: t.Union[str, pathlib.Path] = UNIHAN_URL
    destination: pathlib.Path = DESTINATION_DIR / "unihan.{ext}"
    zip_path: pathlib.Path = UNIHAN_ZIP_PATH
    work_dir: pathlib.Path = WORK_DIR
    fields: t.Sequence[str] = dataclasses.field(
        default_factory=lambda: INDEX_FIELDS + UNIHAN_FIELDS
    )
    format: t.Literal["json", "csv", "yaml", "python"] = "csv"
    input_files: t.List[str] = dataclasses.field(default_factory=lambda: UNIHAN_FILES)
    download: bool = False
    expand: bool = True
    prune_empty: bool = True
    cache: bool = True
    log_level: "LogLevel" = "INFO"

    def __post_init__(self) -> None:
        self.destination = pathlib.Path(str(self.destination).format(ext=self.format))
