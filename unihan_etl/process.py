#!/usr/bin/env python
"""Build Unihan into tabular / structured format and export it."""
import argparse
import codecs
import csv
import fileinput
import glob
import json
import logging
import os
import pathlib
import shutil
import sys
import typing as t
import zipfile
from typing import List, Mapping, Sequence, Union
from urllib.request import urlretrieve

from appdirs import AppDirs

from unihan_etl import expansion
from unihan_etl.__about__ import (
    __author__,
    __description__,
    __package_name__,
    __title__,
    __version__,
)
from unihan_etl.constants import INDEX_FIELDS, UNIHAN_MANIFEST
from unihan_etl.types import (
    ColumnData,
    ColumnDataTuple,
    ExpandedExport,
    ListifiedExport,
    OptionsDict,
    ReportHookFn,
    UntypedNormalizedData,
    UntypedUnihanData,
)
from unihan_etl.util import _dl_progress, merge_dict, ucn_to_unicode

if t.TYPE_CHECKING:
    # try:
    #     from typing import TypeGuard
    # except ImportError:
    #     from typing_extensions import TypeGuard
    from typing_extensions import TypeGuard


log = logging.getLogger(__name__)

dirs = AppDirs(__package_name__, __author__)  # appname  # app author


def not_junk(line: str) -> bool:
    """Return False on newlines and C-style comments."""
    return line[0] != "#" and line != "\n"


def in_fields(
    c: str,
    fields: t.Sequence[str],
) -> bool:
    """Return True if string is in the default fields."""
    return c in tuple(fields) + INDEX_FIELDS


def get_fields(d: UntypedUnihanData) -> t.List[str]:
    """Return list of fields from dict of {filename: ['field', 'field1']}."""
    return sorted({c for cs in d.values() for c in cs})


def filter_manifest(
    files: t.List[str],
) -> UntypedUnihanData:
    """Return filtered :attr:`~.UNIHAN_MANIFEST` from list of file names."""
    return {f: UNIHAN_MANIFEST[f] for f in files}


def files_exist(path: str, files: List[str]) -> bool:
    """Return True if all files exist in specified path."""
    return all(os.path.exists(os.path.join(path, f)) for f in files)


#: Return list of files from list of fields.
def get_files(fields: t.Sequence[str]) -> List[str]:
    files = set()

    for field in fields:
        if field in UNIHAN_FIELDS:
            for file_, file_fields in UNIHAN_MANIFEST.items():
                if any(file_ for h in fields if h in file_fields):
                    files.add(file_)
        else:
            raise KeyError(f"Field {field} not found in file list.")

    return list(files)


#: Directory to use for processing intermittent files.
WORK_DIR = os.path.join(dirs.user_cache_dir, "downloads")
#: Default Unihan Files
UNIHAN_FILES = list(UNIHAN_MANIFEST.keys())
#: URI of Unihan.zip data.
UNIHAN_URL = "http://www.unicode.org/Public/UNIDATA/Unihan.zip"
#: Filepath to output built CSV file to.
DESTINATION_DIR = dirs.user_data_dir
#: Filepath to download Zip file.
UNIHAN_ZIP_PATH = os.path.join(WORK_DIR, "Unihan.zip")
#: Default Unihan fields
UNIHAN_FIELDS: ColumnDataTuple = tuple(get_fields(UNIHAN_MANIFEST))
#: Allowed export types
ALLOWED_EXPORT_TYPES = ["json", "csv"]
try:
    import yaml

    ALLOWED_EXPORT_TYPES += ["yaml"]
except ImportError:
    pass


DEFAULT_OPTIONS: OptionsDict = {
    "source": UNIHAN_URL,
    "destination": "%s/unihan.{ext}" % DESTINATION_DIR,
    "zip_path": UNIHAN_ZIP_PATH,
    "work_dir": WORK_DIR,
    "fields": INDEX_FIELDS + UNIHAN_FIELDS,
    "format": "csv",
    "input_files": UNIHAN_FILES,
    "download": False,
    "expand": True,
    "prune_empty": True,
    "cache": True,
    "log_level": "INFO",
}


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
        help="URL or path of zipfile. Default: %s" % UNIHAN_URL,
    )
    parser.add_argument(
        "-z",
        "--zip-path",
        dest="zip_path",
        help="Path the zipfile is downloaded to. Default: %s" % UNIHAN_ZIP_PATH,
    )
    parser.add_argument(
        "-d",
        "--destination",
        dest="destination",
        help="Output of .csv. Default: %s/unihan.{json,csv,yaml}" % DESTINATION_DIR,
    )
    parser.add_argument(
        "-w", "--work-dir", dest="work_dir", help="Default: %s" % WORK_DIR
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="format",
        choices=ALLOWED_EXPORT_TYPES,
        help="Default: %s" % DEFAULT_OPTIONS["format"],
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
            "All fields used by default. Fields: %s" % ", ".join(UNIHAN_FIELDS)
        ),
    )
    parser.add_argument(
        "-i",
        "--input-files",
        dest="input_files",
        nargs="*",
        help=(
            "Files inside zip to pull data from. Separated by spaces. "
            "All files used by default. Files: %s" % ", ".join(UNIHAN_FILES)
        ),
    )
    parser.add_argument(
        "-l",
        "--log_level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser


def has_valid_zip(zip_path: str) -> bool:
    """
    Return True if valid zip exists.

    Parameters
    ----------
    zip_path : str
        absolute path to zip

    Returns
    -------
    bool :
        True if valid zip exists at path
    """

    if os.path.isfile(zip_path):
        if zipfile.is_zipfile(zip_path):
            log.info("Exists, is valid zip. %s" % zip_path)
            return True
        else:
            log.info("Not a valid zip. %s" % zip_path)
            return False
    else:
        log.info("File doesn't exist. %s" % zip_path)
        return False


def zip_has_files(files: List[str], zip_file: zipfile.ZipFile) -> bool:
    """
    Return True if zip has the files inside.

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
    if set(files).issubset(set(zip_file.namelist())):
        return True
    else:
        return False


def download(
    url: str,
    dest: str,
    urlretrieve_fn: t.Any = urlretrieve,
    reporthook: t.Optional[ReportHookFn] = None,
    cache: bool = True,
) -> str:
    """
    Download file at URL to a destination.

    Parameters
    ----------
    url : str
        URL to download from.
    dest : str
        file path where download is to be saved.
    urlretrieve_fn: callable
        function to download file
    reporthook : function
        Function to write progress bar to stdout buffer.

    Returns
    -------
    str :
        destination where file downloaded to.
    """

    datadir = os.path.dirname(dest)
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    def no_unihan_files_exist() -> bool:
        return not glob.glob(os.path.join(datadir, "Unihan*.txt"))

    def not_downloaded() -> bool:
        return not os.path.exists(os.path.join(datadir, "Unihan.zip"))

    if (no_unihan_files_exist() and not_downloaded()) or not cache:

        log.info("Downloading Unihan.zip...")
        log.info(f"{url} to {dest}")
        if os.path.isfile(url):
            shutil.copy(url, dest)
        else:
            urlretrieve_fn(url, dest, reporthook)

    return dest


def load_data(
    files: Sequence[Union[pathlib.Path, str]]
) -> "fileinput.FileInput[t.Any]":
    """
    Extract zip and process information into CSV's.

    Parameters
    ----------
    files : list of str

    Returns
    -------
    str :
        combined data from files
    """

    log.info("Loading data: %s." % ", ".join([str(s) for s in files]))
    raw_data = fileinput.FileInput(
        files=files, openhook=fileinput.hook_encoded("utf-8")
    )
    log.info("Done loading data.")
    return raw_data


def extract_zip(zip_path: str, dest_dir: str) -> zipfile.ZipFile:
    """
    Extract zip file. Return :class:`zipfile.ZipFile` instance.

    Parameters
    ----------
    zip_file : str
        filepath to extract.
    dest_dir : str
        directory to extract to.

    Returns
    -------
    :class:`zipfile.ZipFile` :
        The extracted zip.
    """

    z = zipfile.ZipFile(zip_path)
    log.info("extract_zip dest dir: %s" % dest_dir)
    z.extractall(dest_dir)

    return z


def normalize(
    raw_data: "fileinput.FileInput[t.Any]",
    fields: Sequence[str],
) -> UntypedNormalizedData:
    """
    Return normalized data from a UNIHAN data files.

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
    for idx, line in enumerate(raw_data):
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
            sys.stdout.write("\rProcessing line %i" % (idx))
            sys.stdout.flush()

    if log.isEnabledFor(logging.DEBUG):
        sys.stdout.write("\n")
        sys.stdout.flush()

    return list(items.values())


def expand_delimiters(normalized_data: UntypedNormalizedData) -> ExpandedExport:
    """
    Return expanded multi-value fields in UNIHAN.

    Parameters
    ----------
    normalized_data : list of dict
        Expects data in list of hashes, per :meth:`process.normalize`

    Returns
    -------
    list of dict :
        Items which have fields with delimiters and custom separation rules,
        will  be expanded. Including multi-value fields not using both fields
        (so all fields stay consistent).
    """
    for char in normalized_data:
        for field in char.keys():
            assert isinstance(char, dict)
            if not char[field]:
                continue
            char[field] = expansion.expand_field(field, char[field])

    return normalized_data


def listify(data: UntypedNormalizedData, fields: Sequence[str]) -> ListifiedExport:
    """
    Convert tabularized data to a CSV-friendly list.

    Parameters
    ----------
    data : list of dict
    params : list of str
        keys/columns, e.g. ['kDictionary']
    """
    list_data = [list(fields)]  # Add fields to first row
    # list_data = [fields[:]]  # Add fields to first row
    list_data += [list(r.values()) for r in list(data)]
    return list_data


def export_csv(
    data: UntypedNormalizedData,
    destination: str,
    fields: ColumnData,
) -> None:
    listified_data = listify(data, fields)

    with open(destination, "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(listified_data)
        log.info("Saved output to: %s" % destination)


def export_json(data: UntypedNormalizedData, destination: str) -> None:
    with codecs.open(destination, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Saved output to: %s" % destination)


def export_yaml(data: UntypedNormalizedData, destination: str) -> None:
    with codecs.open(destination, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, stream=f, allow_unicode=True, default_flow_style=False)
        log.info("Saved output to: %s" % destination)


def validate_options(
    options: Mapping[str, t.Any],
) -> "TypeGuard[OptionsDict]":
    assert isinstance(options, dict)
    if "input_files" in options and "fields" not in options:
        # Filter fields when only files specified.
        try:
            options["fields"] = get_fields(filter_manifest(options["input_files"]))
        except KeyError as e:
            raise KeyError(f"File {e} not found in file list.")
    elif "fields" in options and "input_files" not in options:
        # Filter files when only field specified.
        options["input_files"] = get_files(options["fields"])
    elif "fields" in options and "input_files" in options:
        # Filter fields when only files specified.
        fields_in_files = get_fields(filter_manifest(options["input_files"]))

        not_in_field = [
            h
            for h in options["fields"]
            if h not in fields_in_files + list(INDEX_FIELDS)
        ]
        if not_in_field:
            raise KeyError(
                "Field {} not found in file list.".format(", ".join(not_in_field))
            )
    return True


class Packager:
    """Download and generate a tabular release of
    `UNIHAN <http://www.unicode.org/reports/tr38/>`_."""

    def __init__(
        self,
        options: Mapping[str, t.Any],
    ) -> None:
        """
        Parameters
        ----------
        options : dict
            options values to override defaults.
        """
        setup_logger(None, options.get("log_level", DEFAULT_OPTIONS["log_level"]))

        validate_options(options)
        merged_options = merge_dict(DEFAULT_OPTIONS.copy(), options)
        if validate_options(merged_options):
            self.options: OptionsDict = merged_options

    def download(self, urlretrieve_fn: t.Any = urlretrieve) -> None:
        """
        Download raw UNIHAN data if not exists.

        Parameters
        ----------

        urlretrieve_fn : function
            function to download file
        """
        if not has_valid_zip(self.options["zip_path"]) or not self.options["cache"]:
            download(
                self.options["source"],
                self.options["zip_path"],
                urlretrieve_fn=urlretrieve_fn,
                reporthook=_dl_progress,
                cache=self.options["cache"],
            )

        if (
            not files_exist(self.options["work_dir"], self.options["input_files"])
            or not self.options["cache"]
        ):
            extract_zip(self.options["zip_path"], self.options["work_dir"])

    def export(self) -> t.Union[None, UntypedNormalizedData]:  # NOQA: C901
        """Extract zip and process information into CSV's."""

        fields = list(self.options["fields"])
        for k in INDEX_FIELDS:
            if k not in fields:
                # fields = [k] + fields
                fields.insert(0, k)

        files = [
            os.path.join(self.options["work_dir"], f)
            for f in self.options["input_files"]
        ]

        # Replace {ext} with extension to use.
        self.options["destination"] = self.options["destination"].format(
            ext=self.options["format"]
        )

        if not os.path.exists(os.path.dirname(self.options["destination"])):
            os.makedirs(os.path.dirname(self.options["destination"]))

        raw_data = load_data(files=files)
        data = normalize(raw_data, fields)

        # expand data hierarchically
        if self.options["expand"] and self.options["format"] != "csv":
            data = expand_delimiters(data)

            if self.options["prune_empty"]:
                for char in data:
                    if isinstance(char, dict):
                        for field in list(char.keys()):
                            if not char[field]:
                                char.pop(field, None)

        if self.options["format"] == "json":
            export_json(data, self.options["destination"])
        elif self.options["format"] == "csv":
            export_csv(data, self.options["destination"], fields)
        elif self.options["format"] == "yaml":
            export_yaml(data, self.options["destination"])
        elif self.options["format"] == "python":
            return data
        else:
            log.info("Format %s does not exist" % self.options["format"])
        return None

    @classmethod
    def from_cli(cls, argv: Sequence[str]) -> "Packager":
        """
        Create Packager instance from CLI :mod:`argparse` arguments.

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
            return cls({k: v for k, v in vars(args).items() if v is not None})
        except Exception as e:
            sys.exit(e)


def setup_logger(
    logger: t.Optional[logging.Logger] = None, level: str = "DEBUG"
) -> None:
    """
    Setup logging for CLI use.

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
