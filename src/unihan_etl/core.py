#!/usr/bin/env python
"""Build Unihan into tabular / structured format and export it."""
import argparse
import codecs
import csv
import dataclasses
import fileinput
import json
import logging
import pathlib
import shutil
import sys
import typing as t
import zipfile
from urllib.request import urlretrieve

from unihan_etl import expansion
from unihan_etl.__about__ import (
    __description__,
    __title__,
    __version__,
)
from unihan_etl.constants import (
    ALLOWED_EXPORT_TYPES,
    DESTINATION_DIR,
    INDEX_FIELDS,
    UNIHAN_FIELDS,
    UNIHAN_FILES,
    UNIHAN_MANIFEST,
    UNIHAN_URL,
    UNIHAN_ZIP_PATH,
    WORK_DIR,
)
from unihan_etl.options import Options
from unihan_etl.util import _dl_progress, get_fields, ucn_to_unicode

if t.TYPE_CHECKING:
    from typing_extensions import TypeGuard

    from unihan_etl.types import (
        ColumnData,
        ExpandedExport,
        ListifiedExport,
        LogLevel,
        ReportHookFn,
        StrPath,
        UntypedNormalizedData,
        UntypedUnihanData,
        UrlRetrieveFn,
    )


log = logging.getLogger(__name__)


def not_junk(line: str) -> bool:
    """Return False on newlines and C-style comments."""
    return line[0] != "#" and line != "\n"


def in_fields(
    c: str,
    fields: t.Sequence[str],
) -> bool:
    """Return True if string is in the default fields."""
    return c in tuple(fields) + INDEX_FIELDS


def filter_manifest(
    files: t.List[str],
) -> "UntypedUnihanData":
    """Return filtered :attr:`~.UNIHAN_MANIFEST` from list of file names."""
    return {f: UNIHAN_MANIFEST[f] for f in files}


def files_exist(path: pathlib.Path, files: t.List[str]) -> bool:
    """Return True if all files exist in specified path."""
    return all((pathlib.Path(path) / f).exists() for f in files)


class FieldNotFound(Exception):
    def __init__(self, field: str) -> None:
        return super().__init__(f"Field not found in file list: '{field}'")


class FileNotSupported(Exception):
    def __init__(self, field: str) -> None:
        return super().__init__(f"File not supported: '{field}'")


#: Return list of files from list of fields.
def get_files(fields: t.Sequence[str]) -> t.List[str]:
    files = set()

    for field in fields:
        if field in UNIHAN_FIELDS:
            for file_, file_fields in UNIHAN_MANIFEST.items():
                if any(file_ for h in fields if h in file_fields):
                    files.add(file_)
        else:
            raise FieldNotFound(str(field))

    return list(files)


DEFAULT_OPTIONS = Options()


def get_parser() -> argparse.ArgumentParser:
    """
    Return :py:class:`argparse.ArgumentParser` instance for CLI.

    Returns
    -------

    :py:class:`argparse.ArgumentParser` :
        argument parser for CLI use.
    """
    parser = argparse.ArgumentParser(prog=__title__, description=__description__)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-s",
        "--source",
        dest="source",
        help=f"URL or path of zipfile. Default: {UNIHAN_URL}",
    )
    parser.add_argument(
        "-z",
        "--zip-path",
        dest="zip_path",
        help=f"Path the zipfile is downloaded to. Default: {UNIHAN_ZIP_PATH}",
    )
    parser.add_argument(
        "-d",
        "--destination",
        dest="destination",
        help=f"Output of .csv. Default: {DESTINATION_DIR}/unihan.{{json,csv,yaml}}",
    )
    parser.add_argument(
        "-w", "--work-dir", dest="work_dir", help=f"Default: {WORK_DIR}"
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="format",
        choices=ALLOWED_EXPORT_TYPES,
        help=f"Default: {DEFAULT_OPTIONS.format}",
    )
    parser.add_argument(
        "--no-expand",
        dest="expand",
        action="store_false",
        help=(
            "Don't expand values to lists in multi-value UNIHAN fields. "
            + "Doesn't apply to CSVs."
        ),
    )
    parser.add_argument(
        "--no-prune",
        dest="prune_empty",
        action="store_false",
        help=("Don't prune fields with empty keys" + "Doesn't apply to CSVs."),
    )
    parser.add_argument(
        "--no-cache",
        dest="cache",
        action="store_false",
        help=("Don't cache the UNIHAN zip file or CSV outputs."),
    )
    parser.add_argument(
        "-f",
        "--fields",
        dest="fields",
        nargs="*",
        help=(
            "Fields to use in export. Separated by spaces. "
            f"All fields used by default. Fields: {', '.join(UNIHAN_FIELDS)}"
        ),
    )
    parser.add_argument(
        "-i",
        "--input-files",
        dest="input_files",
        nargs="*",
        help=(
            "Files inside zip to pull data from. Separated by spaces. "
            f"All files used by default. Files: {', '.join(UNIHAN_FILES)}"
        ),
    )
    parser.add_argument(
        "-l",
        "--log_level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser


def has_valid_zip(zip_path: "StrPath") -> bool:
    """Return True if valid zip exists.

    Parameters
    ----------
    zip_path : str or pathlib.Path
        absolute path to zip

    Returns
    -------
    bool :
        True if valid zip exists at path
    """
    if not isinstance(zip_path, pathlib.Path):
        zip_path = pathlib.Path(zip_path)

    if not zip_path.is_file():
        log.info(f"Exists, but is not a file: {zip_path}")
        return False

    if zipfile.is_zipfile(zip_path):
        log.info(f"Exists, is valid zip: {zip_path}")
        return True
    else:
        log.info(f"Not a valid zip: {zip_path}")
        return False


def zip_has_files(files: t.List[str], zip_file: zipfile.ZipFile) -> bool:
    """Return True if zip has the files inside.

    Parameters
    ----------
    files : list of str
        files inside zip file
    zip_file : :py:class:`zipfile.ZipFile`

    Returns
    -------
    bool :
        True if files inside of `:py:meth:`zipfile.ZipFile.namelist()`
    """
    return bool(set(files).issubset(set(zip_file.namelist())))


def download(
    url: "StrPath",
    dest: pathlib.Path,
    urlretrieve_fn: "UrlRetrieveFn" = urlretrieve,
    reporthook: t.Optional["ReportHookFn"] = None,
    cache: bool = True,
) -> pathlib.Path:
    """Download file at URL to a destination.

    Parameters
    ----------
    url : str or pathlib.Path
        URL to download from.
    dest : pathlib.Path
        file path where download is to be saved.
    urlretrieve_fn: UrlRetrieveFn
        function to download file
    reporthook : ReportHookFn, Optional
        Function to write progress bar to stdout buffer.

    Returns
    -------
    pathlib.Path :
        destination where file downloaded to.
    """
    if not isinstance(dest, pathlib.Path):
        dest = pathlib.Path(dest)

    data_dir = dest.parent
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)

    def no_unihan_files_exist() -> bool:
        return not data_dir.match("Unihan*.txt")

    def not_downloaded() -> bool:
        return not (data_dir / "Unihan.zip").exists()

    if (no_unihan_files_exist() and not_downloaded()) or not cache:
        log.info("Downloading Unihan.zip...")
        log.info(f"{url} to {dest}")
        if pathlib.Path(url).is_file():
            shutil.copy(url, dest)
        else:
            urlretrieve_fn(str(url), dest, reporthook)

    return pathlib.Path(dest)


def load_data(
    files: t.Sequence[t.Union[pathlib.Path, str]]
) -> "fileinput.FileInput[t.Any]":
    """Extract zip and process information into CSV's.

    Parameters
    ----------
    files : list of str

    Returns
    -------
    str :
        combined data from files
    """
    log.info(f"Loading data: {', '.join([str(s) for s in files])}")
    raw_data = fileinput.FileInput(
        files=files, openhook=fileinput.hook_encoded("utf-8")
    )
    log.info("Done loading data.")

    return raw_data


def extract_zip(zip_path: pathlib.Path, dest_dir: pathlib.Path) -> zipfile.ZipFile:
    """Extract zip file. Return :class:`zipfile.ZipFile` instance.

    Parameters
    ----------
    zip_file : pathlib.Path
        filepath to extract.
    dest_dir : pathlib.Path
        directory to extract to.

    Returns
    -------
    :class:`zipfile.ZipFile` :
        The extracted zip.
    """
    z = zipfile.ZipFile(zip_path)
    log.info(f"extract_zip dest dir: {dest_dir}")
    z.extractall(dest_dir)

    return z


def normalize(
    raw_data: "fileinput.FileInput[t.Any]",
    fields: t.Sequence[str],
) -> "UntypedNormalizedData":
    """Return normalized data from a UNIHAN data files.

    Parameters
    ----------
    raw_data : str
        combined text files from UNIHAN
    fields : list of str
        list of columns to pull

    Returns
    -------
    list :
        list of unihan character information
    """
    log.info("Collecting field data...")
    items = {}
    for _idx, line in enumerate(raw_data):
        if not_junk(line):
            line = line.strip().split("\t")
            if in_fields(line[1], fields):
                item = dict(zip(["ucn", "field", "value"], line))
                char = ucn_to_unicode(item["ucn"])
                if char not in items:
                    items[char] = {}.fromkeys(fields)
                    items[char]["ucn"] = item["ucn"]
                    items[char]["char"] = char
                items[char][item["field"]] = str(item["value"])
        if log.isEnabledFor(logging.DEBUG):
            sys.stdout.write(f"\rProcessing line {id}")
            sys.stdout.flush()

    if log.isEnabledFor(logging.DEBUG):
        sys.stdout.write("\n")
        sys.stdout.flush()

    return list(items.values())


def expand_delimiters(normalized_data: "UntypedNormalizedData") -> "ExpandedExport":
    """Return expanded multi-value fields in UNIHAN.

    Parameters
    ----------
    normalized_data : list of dict
        Expects data in list of hashes, per :meth:`core.normalize`

    Returns
    -------
    list of dict :
        Items which have fields with delimiters and custom separation rules,
        will  be expanded. Including multi-value fields not using both fields
        (so all fields stay consistent).
    """
    for char in normalized_data:
        for field in char:
            assert isinstance(char, dict)
            if not char[field]:
                continue
            char[field] = expansion.expand_field(field, char[field])

    return normalized_data


def listify(
    data: "UntypedNormalizedData", fields: t.Sequence[str]
) -> "ListifiedExport":
    """Convert tabularized data to a CSV-friendly list.

    Parameters
    ----------
    data : list of dict
    params : list of str
        keys/columns, e.g. ['kDictionary']
    """
    list_data = [list(fields)]  # Add fields to first row
    list_data += [list(r.values()) for r in list(data)]
    return list_data


def export_csv(
    data: "UntypedNormalizedData",
    destination: "StrPath",
    fields: "ColumnData",
) -> None:
    listified_data = listify(data, fields)

    with pathlib.Path(destination).open("w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(listified_data)
        log.info(f"Saved output to: {destination}")


def export_json(data: "UntypedNormalizedData", destination: "StrPath") -> None:
    with codecs.open(str(destination), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        log.info(f"Saved output to: {destination}")


def export_yaml(data: "UntypedNormalizedData", destination: "StrPath") -> None:
    import yaml

    with codecs.open(str(destination), "w", encoding="utf-8") as f:
        yaml.safe_dump(data, stream=f, allow_unicode=True, default_flow_style=False)
        log.info(f"Saved output to: {destination}")


def is_default_option(field_name: str, val: t.Any) -> bool:
    return bool(val == getattr(DEFAULT_OPTIONS, field_name, ""))


def validate_options(
    options: Options,
) -> "TypeGuard[Options]":
    if not is_default_option("input_files", options.input_files) and is_default_option(
        "fields", options.fields
    ):
        # Filter fields when only files specified.
        try:
            options.fields = get_fields(filter_manifest(options.input_files))
        except (KeyError, FieldNotFound) as e:
            raise FileNotSupported(str(e)) from e
    elif not is_default_option("fields", options.fields) and is_default_option(
        "input_files", options.input_files
    ):
        # Filter files when only field specified.
        options.input_files = get_files(options.fields)
    elif not is_default_option("fields", options.fields) and not is_default_option(
        "input_files", options.input_files
    ):
        # Filter fields when only files specified.
        fields_in_files = get_fields(filter_manifest(options.input_files))

        not_in_field = [
            h for h in options.fields if h not in fields_in_files + list(INDEX_FIELDS)
        ]
        if not_in_field:
            raise FieldNotFound(", ".join(not_in_field))
    return True


class Packager:
    """Download and generate a tabular release of
    `UNIHAN <http://www.unicode.org/reports/tr38/>`_."""

    options: Options

    def __init__(
        self,
        options: t.Union[Options, "t.Mapping[str, t.Any]"] = DEFAULT_OPTIONS,
    ) -> None:
        """
        Parameters
        ----------
        options : dict or Options
            options values to override defaults.
        """
        if not isinstance(options, Options):
            options = Options(**options)

        validate_options(options)

        setup_logger(logger=None, level=options.log_level or DEFAULT_OPTIONS.log_level)

        merged_options = dataclasses.replace(
            DEFAULT_OPTIONS, **dataclasses.asdict(options)
        )

        self.options = merged_options

    def download(self, urlretrieve_fn: t.Any = urlretrieve) -> None:
        """Download raw UNIHAN data if not exists.

        Parameters
        ----------
        urlretrieve_fn : function
            function to download file
        """
        if not has_valid_zip(self.options.zip_path) or not self.options.cache:
            download(
                url=self.options.source,
                dest=self.options.zip_path,
                urlretrieve_fn=urlretrieve_fn,
                reporthook=_dl_progress,
                cache=self.options.cache,
            )

        if (
            not files_exist(self.options.work_dir, self.options.input_files)
            or not self.options.cache
        ):
            extract_zip(self.options.zip_path, self.options.work_dir)

    def export(self) -> t.Union[None, "UntypedNormalizedData"]:
        """Extract zip and process information into CSV's."""
        fields = list(self.options.fields)
        for k in INDEX_FIELDS:
            if k not in fields:
                fields.insert(0, k)

        files = [
            pathlib.Path(self.options.work_dir) / f for f in self.options.input_files
        ]

        # Replace {ext} with extension to use.
        self.options.destination = pathlib.Path(
            str(self.options.destination).format(ext=self.options.format)
        )

        if not self.options.destination.parent.exists():
            self.options.destination.parent.mkdir(parents=True, exist_ok=True)

        raw_data = load_data(files=files)
        data = normalize(raw_data, fields)

        # expand data hierarchically
        if self.options.expand and self.options.format != "csv":
            data = expand_delimiters(data)

            if self.options.prune_empty:
                for char in data:
                    if isinstance(char, dict):
                        for field in list(char.keys()):
                            if not char[field]:
                                char.pop(field, None)

        if self.options.format == "json":
            export_json(data, self.options.destination)
        elif self.options.format == "csv":
            export_csv(data, self.options.destination, fields)
        elif self.options.format == "yaml":
            export_yaml(data, self.options.destination)
        elif self.options.format == "python":
            return data
        else:
            log.info(f"Format {self.options.format} does not exist")
        return None

    @classmethod
    def from_cli(cls, argv: t.Sequence[str]) -> "Packager":
        """Create Packager instance from CLI :mod:`argparse` arguments.

        Parameters
        ----------
        argv : list
            Arguments passed in via CLI.

        Returns
        -------
        :class:`~.Packager` :
            builder
        """
        parser = get_parser()

        args = parser.parse_args(argv)

        try:
            return cls(
                Options(**{k: v for k, v in vars(args).items() if v is not None})
            )
        except Exception as e:
            sys.exit(str(e))


def setup_logger(
    logger: t.Optional[logging.Logger] = None,
    level: "LogLevel" = "DEBUG",
) -> None:
    """Setup logging for CLI use.

    Parameters
    ----------
    logger : :py:class:`Logger`
        instance of logger
    level : str
        logging level, e.g. 'DEBUG'
    """
    if not logger:
        logger = logging.getLogger()
    if not logger.handlers:
        channel = logging.StreamHandler()

        logger.setLevel(level)
        logger.addHandler(channel)


if __name__ == "__main__":
    p = Packager.from_cli(sys.argv[1:])
    p.download()
    p.export()
