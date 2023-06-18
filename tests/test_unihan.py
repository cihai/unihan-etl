"""Tests for unihan data download and processing."""
import dataclasses
import logging
import pathlib
import shutil
import typing as t
import zipfile
from http.client import HTTPMessage

import pytest

from unihan_etl import constants, core
from unihan_etl.__about__ import __version__
from unihan_etl.constants import UNIHAN_ZIP_PATH
from unihan_etl.core import DEFAULT_OPTIONS, Packager, zip_has_files
from unihan_etl.test import assert_dict_contains_subset
from unihan_etl.types import ColumnData, UntypedNormalizedData
from unihan_etl.options import Options
from unihan_etl.util import get_fields
from .constants import FIXTURE_PATH

if t.TYPE_CHECKING:
    from urllib.request import _DataType
    from unihan_etl.types import StrPath


log = logging.getLogger(__name__)


def test_zip_has_files(mock_zip: zipfile.ZipFile) -> None:
    assert zip_has_files(["Unihan_Readings.txt"], mock_zip)

    assert not zip_has_files(["Unihan_Cats.txt"], mock_zip)


def test_has_valid_zip(tmp_path: pathlib.Path, mock_zip: zipfile.ZipFile) -> None:
    if UNIHAN_ZIP_PATH.is_file():
        assert core.has_valid_zip(UNIHAN_ZIP_PATH)
    else:
        assert not core.has_valid_zip(UNIHAN_ZIP_PATH)

    assert mock_zip.filename is not None

    assert core.has_valid_zip(mock_zip.filename)

    bad_zip = tmp_path / "corrupt.zip"
    bad_zip.write_text("moo", encoding="utf-8")

    assert not core.has_valid_zip(bad_zip)


def test_in_fields() -> None:
    columns = ["hey", "kDefinition", "kWhat"]
    result = core.in_fields("kDefinition", columns)

    assert result


def test_filter_manifest() -> None:
    expected = {
        "Unihan_Variants.txt": [
            "kSemanticVariant",
            "kSimplifiedVariant",
            "kSpecializedSemanticVariant",
            "kTraditionalVariant",
            "kZVariant",
        ]
    }

    result = core.filter_manifest(["Unihan_Variants.txt"])

    assert set(result) == set(expected)


def test_get_files() -> None:
    fields = ["kKorean", "kRSUnicode"]
    expected = ["Unihan_Readings.txt", "Unihan_RadicalStrokeCounts.txt"]

    result = core.get_files(fields)

    assert set(result) == set(expected)


def test_download(
    tmp_path: pathlib.Path,
    mock_zip: zipfile.ZipFile,
    mock_zip_path: pathlib.Path,
    mock_zip_pathname: pathlib.Path,
) -> None:
    dest_path = tmp_path / "data" / mock_zip_pathname
    assert (
        not dest_path.parent.exists() and not dest_path.parent.is_dir()
    ), "Test setup: Should not exist yet, core.download() should create them!"

    def urlretrieve(
        url: str,
        filename: t.Optional["StrPath"] = None,
        reporthook: t.Optional[t.Callable[[int, int, int], object]] = None,
        data: "_DataType" = None,
    ) -> t.Tuple[str, "HTTPMessage"]:
        shutil.copy(str(mock_zip_path), str(dest_path))
        return (
            "",
            HTTPMessage(),
        )

    core.download(url=mock_zip_path, dest=dest_path, urlretrieve_fn=urlretrieve)

    assert (
        dest_path.parent.exists() and dest_path.parent.is_dir()
    ), "Creates data's parent directory if doesn't exist."


def test_download_mock(
    tmp_path: pathlib.Path,
    mock_zip: zipfile.ZipFile,
    mock_zip_path: pathlib.Path,
    mock_test_dir: pathlib.Path,
    test_options: Options,
) -> None:
    data_path = tmp_path / "data"
    dest_path = data_path / "data" / "hey.zip"

    def urlretrieve(
        url: str,
        filename: t.Optional["StrPath"] = None,
        reporthook: t.Optional[t.Callable[[int, int, int], object]] = None,
        data: "_DataType" = None,
    ) -> t.Tuple[str, "HTTPMessage"]:
        shutil.copy(mock_zip_path, dest_path)
        return (
            "",
            HTTPMessage(),
        )

    p = Packager(
        dataclasses.replace(
            test_options,
            **{
                "fields": ["kDefinition"],
                "zip_path": dest_path,
                "work_dir": mock_test_dir / "downloads",
                "destination": data_path / "unihan.csv",
            },
        )
    )
    p.download(urlretrieve_fn=urlretrieve)
    assert dest_path.exists()
    p.export()


def test_export_format(
    tmp_path: pathlib.Path,
    mock_zip: zipfile.ZipFile,
    mock_zip_path: pathlib.Path,
    mock_test_dir: pathlib.Path,
    test_options: Options,
) -> None:
    data_path = tmp_path / "data"
    dest_path = data_path / "data" / "hey.zip"

    def urlretrieve(
        url: str,
        filename: t.Optional["StrPath"] = None,
        reporthook: t.Optional[t.Callable[[int, int, int], object]] = None,
        data: "_DataType" = None,
    ) -> t.Tuple[str, "HTTPMessage"]:
        shutil.copy(str(mock_zip_path), str(dest_path))
        return ("", HTTPMessage())

    p = Packager(
        dataclasses.replace(
            test_options,
            **{
                "fields": ["kDefinition"],
                "zip_path": dest_path,
                "work_dir": str(mock_test_dir / "downloads"),
                "destination": str(data_path / "unihan.{ext}"),
                "format": "json",
            },
        ),
    )
    p.download(urlretrieve_fn=urlretrieve)
    assert dest_path.exists()
    p.export()
    assert data_path / "unihan.json" == p.options.destination
    assert p.options.destination.exists()


def test_extract_zip(
    mock_zip: zipfile.ZipFile, mock_zip_path: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    zf = core.extract_zip(zip_path=mock_zip_path, dest_dir=tmp_path)

    assert len(zf.infolist()) == 1
    assert zf.infolist()[0].file_size == 218
    assert zf.infolist()[0].filename == "Unihan_Readings.txt"


def test_normalize_only_output_requested_columns(
    normalized_data: UntypedNormalizedData, columns: ColumnData
) -> None:
    in_columns = ["kDefinition", "kCantonese"]

    for data_labels in normalized_data:
        assert set(columns) == set(data_labels.keys())

    items = core.listify(normalized_data, in_columns)
    example_result = items[0]

    not_in_columns: t.List[str] = []

    # columns not selected in normalize must not be in result.
    for v in example_result:
        if v not in columns:
            not_in_columns.append(v)
        else:
            in_columns.append(v)

    assert [] == not_in_columns, "normalize filters columns not specified."
    assert set(in_columns).issubset(
        set(columns)
    ), "normalize returns correct columns specified + ucn and char."


def test_normalize_simple_data_format() -> None:
    """normalize turns data into simple data format (SDF)."""
    csv_files = [
        FIXTURE_PATH / "Unihan_DictionaryLikeData.txt",
        FIXTURE_PATH / "Unihan_Readings.txt",
    ]

    columns = (
        "kTotalStrokes",
        "kPhonetic",
        "kCantonese",
        "kDefinition",
    ) + constants.INDEX_FIELDS

    data = core.load_data(files=csv_files)

    normalized_items = core.normalize(data, columns)
    items = core.listify(normalized_items, columns)

    header = items[0]
    assert set(header) == set(columns)

    rows = items[1:]  # NOQA


def test_flatten_fields() -> None:
    single_dataset = {"Unihan_Readings.txt": ["kCantonese", "kDefinition", "kHangul"]}

    expected = ["kCantonese", "kDefinition", "kHangul"]
    results = get_fields(single_dataset)

    assert expected == results

    datasets = {
        "Unihan_NumericValues.txt": [
            "kAccountingNumeric",
            "kOtherNumeric",
            "kPrimaryNumeric",
        ],
        "Unihan_OtherMappings.txt": ["kBigFive", "kCCCII", "kCNS1986"],
    }

    expected = [
        "kAccountingNumeric",
        "kOtherNumeric",
        "kPrimaryNumeric",
        "kBigFive",
        "kCCCII",
        "kCNS1986",
    ]

    results = get_fields(datasets)

    assert set(expected) == set(results)


def test_pick_files(mock_zip_path: pathlib.Path) -> None:
    """Pick a white list of files to build from."""

    files = ["Unihan_Readings.txt", "Unihan_Variants.txt"]

    options = Options(input_files=files, zip_path=mock_zip_path)

    b = core.Packager(options)

    result = b.options.input_files
    expected = files

    assert result == expected, "Returns only the files picked."


def test_raise_error_unknown_field() -> None:
    """Throw error if picking unknown field."""

    options = Options(fields=["kHello"])

    with pytest.raises(KeyError) as excinfo:
        core.Packager(options)
    excinfo.match("Field ([a-zA-Z].*) not found in file list.")


def test_raise_error_unknown_file() -> None:
    """Throw error if picking unknown file."""

    options = Options(input_files=["Sparta.lol"])

    with pytest.raises(KeyError) as excinfo:
        core.Packager(options)
    excinfo.match(r"File ([a-zA-Z_\.\'].*) not found in file list.")


def test_raise_error_unknown_field_filtered_files() -> None:
    """Throw error field not in file list, when files specified."""

    files = ["Unihan_Variants.txt"]

    options = Options(input_files=files, fields=["kDefinition"])

    with pytest.raises(KeyError) as excinfo:
        core.Packager(options)
    excinfo.match("Field ([a-zA-Z].*) not found in file list.")


def test_set_reduce_files_automatically_when_only_field_specified() -> None:
    """Picks file automatically if none specified and fields are."""

    fields = (
        constants.UNIHAN_MANIFEST["Unihan_Readings.txt"]
        + constants.UNIHAN_MANIFEST["Unihan_Variants.txt"]
    )

    options = Options(fields=fields)

    b = core.Packager(options)

    expected = ["Unihan_Readings.txt", "Unihan_Variants.txt"]
    results = b.options.input_files

    assert set(expected) == set(results)


def test_set_reduce_fields_automatically_when_only_files_specified() -> None:
    """Picks only necessary files when fields specified."""

    files = ["Unihan_Readings.txt", "Unihan_Variants.txt"]

    options = Options(input_files=files)

    b = core.Packager(options)

    results = get_fields(core.filter_manifest(files))
    expected = b.options.fields

    assert set(expected) == set(results), "Returns only the fields for files picked."


def test_no_args() -> None:
    """Works without arguments."""

    assert DEFAULT_OPTIONS == Packager.from_cli([]).options


def test_cli_plus_defaults(mock_zip_path: pathlib.Path) -> None:
    """Test CLI args + defaults."""

    option_subset = {"zip_path": str(mock_zip_path)}
    pkgr = Packager.from_cli(["-z", str(mock_zip_path)])
    assert_dict_contains_subset(option_subset, dataclasses.asdict(pkgr.options))

    option_subset_one_field = {"fields": ["kDefinition"]}
    pkgr = Packager.from_cli(["-f", "kDefinition"])
    assert_dict_contains_subset(
        option_subset_one_field, dataclasses.asdict(pkgr.options)
    )

    option_subset_two_fields = {"fields": ["kDefinition", "kXerox"]}
    pkgr = Packager.from_cli(["-f", "kDefinition", "kXerox"])
    assert_dict_contains_subset(
        option_subset_two_fields,
        dataclasses.asdict(pkgr.options),
        msg="fields -f allows multiple fields.",
    )

    option_subset_with_destination = {
        "fields": ["kDefinition", "kXerox"],
        "destination": pathlib.Path("data/ha.csv"),
    }
    pkgr = Packager.from_cli(["-f", "kDefinition", "kXerox", "-d", "data/ha.csv"])
    assert_dict_contains_subset(
        option_subset_with_destination,
        dataclasses.asdict(pkgr.options),
        msg="fields -f allows additional arguments.",
    )

    pkgr = Packager.from_cli(["--format", "json"])
    option_subset = {"format": "json"}
    assert_dict_contains_subset(
        option_subset, dataclasses.asdict(pkgr.options), msg="format argument works"
    )


def test_cli_exit_emessage_to_stderr() -> None:
    """Sends exception .message to stderr on exit."""

    # SystemExit print's to stdout by default
    with pytest.raises(SystemExit) as excinfo:
        Packager.from_cli(["-d", "data/output.csv", "-f", "sdfa"])

    excinfo.match("Field sdfa not found in file list.")


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_cli_version(capsys: pytest.CaptureFixture[str], flag: str) -> None:
    with pytest.raises(SystemExit):
        Packager.from_cli([flag])
    captured = capsys.readouterr()

    assert __version__ in captured.out
