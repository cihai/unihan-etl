import pathlib
import zipfile
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

from unihan_etl import constants, process
from unihan_etl.process import DEFAULT_OPTIONS, Packager
from unihan_etl.util import merge_dict

from .constants import FIXTURE_PATH


@pytest.fixture
def test_options() -> Dict[
    str,
    Union[
        str,
        Tuple[str, ...],
        List[str],
        bool,
    ],
]:
    return merge_dict(DEFAULT_OPTIONS.copy(), {"input_files": ["Unihan_Readings.txt"]})


@pytest.fixture(scope="session")
def mock_zip_pathname() -> str:
    return "Unihan.zip"


@pytest.fixture(scope="session")
def fixture_files() -> List[pathlib.Path]:
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
def sample_data2(fixture_files):
    return process.load_data(files=fixture_files)


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
def TestPackager(mock_test_dir, mock_zip_path):
    # monkey-patching builder
    options = {
        "work_dir": str(mock_test_dir),
        "zip_path": str(mock_zip_path),
        "destination": str(mock_test_dir / "unihan.csv"),
    }
    return Packager(options)


@pytest.fixture(scope="session")
def columns() -> Tuple[str, ...]:
    return (
        constants.CUSTOM_DELIMITED_FIELDS
        + constants.INDEX_FIELDS
        + constants.SPACE_DELIMITED_FIELDS
    )


@pytest.fixture(scope="session")
def normalized_data(
    columns: Tuple[str, ...],
    fixture_files: List[pathlib.Path],
) -> List[Dict[str, Optional[str]]]:
    data = process.load_data(files=fixture_files)

    return process.normalize(data, columns)


@pytest.fixture(scope="session")
def expanded_data(
    normalized_data: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Any]]:
    return process.expand_delimiters(normalized_data)


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
