import contextlib
import getpass
import logging
import os
import pathlib
import typing as t
import zipfile

import pytest
from appdirs import AppDirs as BaseAppDirs

from unihan_etl import constants, core
from unihan_etl._internal.app_dirs import AppDirs
from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

logger = logging.getLogger(__name__)
USING_ZSH = "zsh" in os.getenv("SHELL", "")

PROJECT_PATH = pathlib.Path(__file__).parent.parent.parent
TESTS_PATH = PROJECT_PATH / "tests"
SAMPLE_FIXTURE_PATH = TESTS_PATH / "fixtures"

app_dirs = AppDirs(_app_dirs=BaseAppDirs("pytest-cihai", "cihai team"))


@pytest.fixture(scope="session")
def user_cache_path() -> pathlib.Path:
    """Override this to destination of your choice."""
    return app_dirs.user_cache_dir


@pytest.fixture(scope="session")
def project_cache_path() -> pathlib.Path:
    """Override this to destination of your choice."""
    return PROJECT_PATH / ".unihan_cache"


@pytest.fixture(scope="session")
def cache_path(project_cache_path: pathlib.Path) -> pathlib.Path:
    """Override this to destination of your choice."""
    return project_cache_path


@pytest.fixture(scope="session")
def fixture_root(cache_path: pathlib.Path) -> pathlib.Path:
    return cache_path / "f"


@pytest.fixture(scope="session")
def full_unihan_path(fixture_root: pathlib.Path) -> pathlib.Path:
    return fixture_root / "full"


@pytest.fixture(scope="session")
def full_unihan_options(full_unihan_path: pathlib.Path) -> UnihanOptions:
    return UnihanOptions(
        work_dir=full_unihan_path / "work",
        zip_path=full_unihan_path / "downloads" / "Unihan.zip",
        destination=full_unihan_path / "out" / "unihan.csv",
    )


@pytest.fixture(scope="session")
def full_unihan_packager(
    full_unihan_path: pathlib.Path, full_unihan_options: "UnihanOptions"
) -> "Packager":
    """Setup a tiny portion of UNIHAN, return a UnihanOptions."""
    return Packager(full_unihan_options)


@pytest.fixture(scope="session")
def ensure_full_unihan(
    full_unihan_path: pathlib.Path,
    full_unihan_options: "UnihanOptions",
    full_unihan_packager: "Packager",
) -> None:
    """Downloads and extracts a full UNIHAN, return a UnihanOptions.

    TODO: Allow setting up various scenarios, e.g. download only, broken download, etc.
    """
    pkgr = Packager(full_unihan_options)
    pkgr.download()

    if not pkgr.options.destination.exists():
        pkgr.export()

    return None


@pytest.fixture(scope="session")
def quick_unihan_path(fixture_root: pathlib.Path) -> pathlib.Path:
    return fixture_root / "quick"


@pytest.fixture(scope="session")
def quick_unihan_zip_path(quick_unihan_path: pathlib.Path) -> pathlib.Path:
    return quick_unihan_path / "downloads" / "Unihan.zip"


@pytest.fixture(scope="session")
def quick_unihan_zip(
    quick_unihan_path: pathlib.Path,
    quick_unihan_zip_path: pathlib.Path,
    sample_fixture_files: t.List[pathlib.Path],
) -> zipfile.ZipFile:
    _files = []
    for f in sample_fixture_files:
        _files += [f]

    with contextlib.suppress(FileExistsError):
        quick_unihan_zip_path.parent.mkdir(parents=True)

    zf = zipfile.ZipFile(quick_unihan_zip_path, "a")
    for _f in sample_fixture_files:
        if _f.name not in zf.namelist():
            zf.write(_f, _f.name)
    zf.close()

    return zf


@pytest.fixture(scope="session")
def quick_unihan_options(
    quick_unihan_path: pathlib.Path,
    quick_unihan_zip: zipfile.ZipFile,
    quick_unihan_zip_path: pathlib.Path,
) -> UnihanOptions:
    return UnihanOptions(
        work_dir=quick_unihan_path / "work",
        zip_path=quick_unihan_zip_path,
        destination=quick_unihan_path / "out" / "unihan.csv",
    )


@pytest.fixture(scope="session")
def quick_unihan_packager(
    quick_unihan_path: pathlib.Path, quick_unihan_options: "UnihanOptions"
) -> "Packager":
    """Setup a tiny portion of UNIHAN, return a UnihanOptions."""
    return Packager(quick_unihan_options)


@pytest.fixture(scope="session")
def ensure_quick_unihan(
    quick_unihan_path: pathlib.Path,
    quick_unihan_options: "UnihanOptions",
    quick_unihan_packager: "Packager",
) -> None:
    """Setup a tiny portion of UNIHAN, return a UnihanOptions."""
    pkgr = Packager(quick_unihan_options)
    pkgr.download()

    if not pkgr.options.destination.exists():
        pkgr.export()

    return None


@pytest.fixture(scope="session")
def bootstrap_all(ensure_full_unihan: None, ensure_quick_unihan: None) -> None:
    """This should be used like so in your project's conftest.py:

    >>> import pytest
    >>> @pytest.fixture(scope="session", autouse=True)
    ... def bootstrap(bootstrap_all) -> None:
    ...     return None
    """
    return None


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
def test_options() -> t.Union[UnihanOptions, t.Mapping[str, t.Any]]:
    return UnihanOptions(input_files=["Unihan_Readings.txt"])


@pytest.fixture(scope="session")
def mock_zip_pathname() -> str:
    return "Unihan.zip"


@pytest.fixture(scope="session")
def sample_fixture_files() -> t.List[pathlib.Path]:
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
    return [SAMPLE_FIXTURE_PATH / f for f in files]


@pytest.fixture(scope="session")
def mock_test_dir(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    return tmp_path_factory.mktemp("unihan_etl")


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
        UnihanOptions(
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
def sample_normalized_data(
    columns: "ColumnData",
    sample_fixture_files: t.List[pathlib.Path],
) -> "UntypedNormalizedData":
    data = core.load_data(files=sample_fixture_files)

    return core.normalize(data, columns)


@pytest.fixture(scope="session")
def sample_expanded_data(
    sample_normalized_data: t.List[t.Dict[str, t.Any]]
) -> "ExpandedExport":
    return core.expand_delimiters(sample_normalized_data)


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
