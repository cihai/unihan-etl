import getpass
import logging
import os
import pathlib
import typing as t

import pytest

import fileinput
import zipfile

from unihan_etl import constants, core
from unihan_etl.core import Packager
from unihan_etl.options import Options

logger = logging.getLogger(__name__)
USING_ZSH = "zsh" in os.getenv("SHELL", "")

TESTS_PATH = pathlib.Path(__file__).parent.parent.parent / "tests"
FIXTURE_PATH = TESTS_PATH / "fixtures"


@pytest.fixture(scope="session")
def home_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Temporary `/home/` path."""
    return tmp_path_factory.mktemp("home")


@pytest.fixture(scope="session")
def home_user_name() -> str:
    """Default username to set for :func:`user_path` fixture."""
    return getpass.getuser()


@pytest.fixture(scope="session")
def user_path(home_path: pathlib.Path, home_user_name: str) -> pathlib.Path:
    """Default temporary user directory.

    Used by: :func:`zshrc`

    Note: You will need to set the home directory, see :ref:`set_home`.
    """
    p = home_path / home_user_name
    p.mkdir()
    return p


@pytest.mark.skipif(USING_ZSH, reason="Using ZSH")
@pytest.fixture(scope="session")
def zshrc(user_path: pathlib.Path) -> pathlib.Path:
    """This quiets ZSH default message.

    Needs a startup file .zshenv, .zprofile, .zshrc, .zlogin.
    """
    p = user_path / ".zshrc"
    p.touch()
    return p


if t.TYPE_CHECKING:
    from unihan_etl.types import (
        ColumnData,
        ExpandedExport,
        UntypedNormalizedData,
    )


@pytest.fixture
def test_options() -> t.Union[Options, t.Mapping[str, t.Any]]:
    return Options(input_files=["Unihan_Readings.txt"])


@pytest.fixture(scope="session")
def mock_zip_pathname() -> str:
    return "Unihan.zip"


@pytest.fixture(scope="session")
def fixture_files() -> t.List[pathlib.Path]:
    files = [
        "Unihan_DictionaryIndices.txt",
        "Unihan_DictionaryLikeData.txt",
        "Unihan_IRGSources.txt",
        "Unihan_NumericValues.txt",
        "Unihan_OtherMappings.txt",
        "Unihan_RadicalStrokeCounts.txt",
        "Unihan_Readings.txt",
        "Unihan_Variants.txt",
    ]
    return [FIXTURE_PATH / f for f in files]


@pytest.fixture(scope="session")
def sample_data2(fixture_files: t.List[pathlib.Path]) -> "fileinput.FileInput[t.Any]":
    return core.load_data(files=fixture_files)


@pytest.fixture(scope="session")
def mock_test_dir(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    unihan_etl_path = tmp_path_factory.mktemp("unihan_etl")
    return unihan_etl_path


@pytest.fixture(scope="session")
def mock_zip_path(mock_test_dir: pathlib.Path, mock_zip_pathname: str) -> pathlib.Path:
    return mock_test_dir / mock_zip_pathname


@pytest.fixture(scope="session")
def mock_zip(mock_zip_path: pathlib.Path, sample_data: str) -> zipfile.ZipFile:
    zf = zipfile.ZipFile(str(mock_zip_path), "a")
    zf.writestr("Unihan_Readings.txt", sample_data.encode("utf-8"))
    zf.close()
    return zf


@pytest.fixture(scope="session")
def TestPackager(mock_test_dir: pathlib.Path, mock_zip_path: pathlib.Path) -> Packager:
    # monkey-patching builder
    return Packager(
        Options(
            work_dir=mock_test_dir,
            zip_path=mock_zip_path,
            destination=mock_test_dir / "unihan.csv",
        )
    )


@pytest.fixture(scope="session")
def columns() -> "ColumnData":
    return (
        constants.CUSTOM_DELIMITED_FIELDS
        + constants.INDEX_FIELDS
        + constants.SPACE_DELIMITED_FIELDS
    )


@pytest.fixture(scope="session")
def normalized_data(
    columns: "ColumnData",
    fixture_files: t.List[pathlib.Path],
) -> "UntypedNormalizedData":
    data = core.load_data(files=fixture_files)

    return core.normalize(data, columns)


@pytest.fixture(scope="session")
def expanded_data(normalized_data: t.List[t.Dict[str, t.Any]]) -> "ExpandedExport":
    return core.expand_delimiters(normalized_data)


@pytest.fixture(scope="session")
def sample_data() -> str:
    return """\
U+3400	kCantonese	jau1
U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
U+3400	kMandarin	qiū
U+3401	kCantonese	tim2
U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
U+3401	kHanyuPinyin	10019.020:tiàn
"""
