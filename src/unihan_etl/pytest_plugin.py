import contextlib
import getpass
import logging
import os
import pathlib
import typing as t
import zipfile

import pytest
from appdirs import AppDirs as BaseAppDirs

import unihan_etl
from unihan_etl import constants, core
from unihan_etl._internal.app_dirs import AppDirs
from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

logger = logging.getLogger(__name__)

USING_ZSH = "zsh" in os.getenv("SHELL", "")

UNIHAN_ETL_PATH = pathlib.Path(unihan_etl.__file__).parent
PROJECT_PATH = UNIHAN_ETL_PATH.parent.parent
TESTS_PATH = PROJECT_PATH / "tests"
DATA_FIXTURE_PATH = UNIHAN_ETL_PATH / "data_files"
QUICK_FIXTURE_PATH = DATA_FIXTURE_PATH / "quick"

app_dirs = AppDirs(_app_dirs=BaseAppDirs("pytest-cihai", "cihai team"))


@pytest.fixture(scope="session")
def unihan_user_cache_path() -> pathlib.Path:
    """Override this to destination of your choice."""
    return app_dirs.user_cache_dir


@pytest.fixture(scope="session")
def unihan_project_cache_path() -> pathlib.Path:
    """Override this to destination of your choice."""
    return PROJECT_PATH / ".unihan_cache"


@pytest.fixture(scope="session")
def unihan_cache_path(unihan_project_cache_path: pathlib.Path) -> pathlib.Path:
    """Override this to destination of your choice."""
    return unihan_project_cache_path


@pytest.fixture(scope="session")
def unihan_fixture_root(unihan_cache_path: pathlib.Path) -> pathlib.Path:
    return unihan_cache_path / "f"


@pytest.fixture(scope="session")
def unihan_full_path(unihan_fixture_root: pathlib.Path) -> pathlib.Path:
    return unihan_fixture_root / "full"


@pytest.fixture(scope="session")
def unihan_full_options(unihan_full_path: pathlib.Path) -> UnihanOptions:
    return UnihanOptions(
        work_dir=unihan_full_path / "work",
        zip_path=unihan_full_path / "downloads" / "Unihan.zip",
        destination=unihan_full_path / "out" / "unihan.csv",
    )


@pytest.fixture(scope="session")
def unihan_full_packager(
    unihan_full_path: pathlib.Path, unihan_full_options: "UnihanOptions"
) -> "Packager":
    """Setup a tiny portion of UNIHAN, return a UnihanOptions."""
    return Packager(unihan_full_options)


@pytest.fixture(scope="session")
def unihan_ensure_full(
    unihan_full_path: pathlib.Path,
    unihan_full_options: "UnihanOptions",
    unihan_full_packager: "Packager",
) -> None:
    """Downloads and extracts a full UNIHAN, return a UnihanOptions.

    >>> import pathlib

    >>> from unihan_etl.core import Packager
    >>> from unihan_etl.options import Options as UnihanOptions

    >>> def test_unihan_ensure_full(
    ...     unihan_full_path: pathlib.Path,
    ...     unihan_full_options: "UnihanOptions",
    ...     unihan_full_packager: "Packager",
    ... ) -> None:
    ...     unihan_full_destination = unihan_full_options.destination
    ...     assert unihan_full_destination.exists()
    ...     assert unihan_full_destination.stat().st_size > 20_000_000
    ...
    ...     assert unihan_full_options.work_dir.exists()
    ...     unihan_readings = unihan_full_options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size > 6200000

    .. ::
        >>> locals().keys()
        dict_keys(...)

        >>> source = ''.join([e.source for e in request._pyfuncitem.dtest.examples][:4])
        >>> pytester = request.getfixturevalue('pytester')

        >>> pytester.makepyfile(**{'whatever.py': source})
        PosixPath(...)

        >>> result = pytester.runpytest('whatever.py', '--disable-warnings')
        ===...

        >>> result.assert_outcomes(passed=1)

    Extending fixtures:

    >>> import pathlib

    >>> import pytest

    >>> from unihan_etl.core import Packager
    >>> from unihan_etl.options import Options as UnihanOptions

    >>> @pytest.fixture
    ... def my_unihan(
    ...     unihan_full_path: pathlib.Path,
    ...     unihan_full_options: "UnihanOptions",
    ...     unihan_full_packager: "Packager",
    ... ) -> "Packager":
    ...     return unihan_full_packager

    >>> def test_my_extended_unihan_Fixture(my_unihan: "Packager") -> None:
    ...     my_unihan.download()
    ...     my_unihan_destination = my_unihan.options.destination
    ...     if not my_unihan_destination.exists():
    ...         my_unihan.export()
    ...     assert my_unihan_destination.exists()
    ...     assert my_unihan_destination.stat().st_size > 20_000_000
    ...
    ...     assert my_unihan.options.work_dir.exists()
    ...     unihan_readings = my_unihan.options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size > 6200000

    .. ::
        >>> locals().keys()
        dict_keys(...)

        >>> source = ''.join([
        ...     e.source for e in request._pyfuncitem.dtest.examples][10:16]
        ... )
        >>> pytester = request.getfixturevalue('pytester')

        >>> pytester.makepyfile(**{'example_2.py': source})
        PosixPath(...)

        >>> result = pytester.runpytest('example_2.py', '--disable-warnings')
        ===...

        >>> result.assert_outcomes(passed=1)
    """
    pkgr = Packager(unihan_full_options)
    pkgr.download()

    if not pkgr.options.destination.exists():
        pkgr.export()

    return None


@pytest.fixture(scope="session")
def unihan_quick_path(unihan_fixture_root: pathlib.Path) -> pathlib.Path:
    return unihan_fixture_root / "quick"


@pytest.fixture(scope="session")
def unihan_quick_zip_path(unihan_quick_path: pathlib.Path) -> pathlib.Path:
    return unihan_quick_path / "downloads" / "Unihan.zip"


@pytest.fixture(scope="session")
def unihan_quick_zip(
    unihan_quick_path: pathlib.Path,
    unihan_quick_zip_path: pathlib.Path,
    unihan_quick_fixture_files: t.List[pathlib.Path],
) -> zipfile.ZipFile:
    _files = []
    for f in unihan_quick_fixture_files:
        _files += [f]

    with contextlib.suppress(FileExistsError):
        unihan_quick_zip_path.parent.mkdir(parents=True)

    zf = zipfile.ZipFile(unihan_quick_zip_path, "a")
    for _f in unihan_quick_fixture_files:
        if _f.name not in zf.namelist():
            zf.write(_f, _f.name)
    zf.close()

    return zf


@pytest.fixture(scope="session")
def unihan_quick_options(
    unihan_quick_path: pathlib.Path,
    unihan_quick_zip: zipfile.ZipFile,
    unihan_quick_zip_path: pathlib.Path,
) -> UnihanOptions:
    return UnihanOptions(
        work_dir=unihan_quick_path / "work",
        zip_path=unihan_quick_zip_path,
        destination=unihan_quick_path / "out" / "unihan.csv",
    )


@pytest.fixture(scope="session")
def unihan_quick_packager(
    unihan_quick_path: pathlib.Path, unihan_quick_options: "UnihanOptions"
) -> "Packager":
    """Setup a tiny portion of UNIHAN, return a UnihanOptions."""
    return Packager(unihan_quick_options)


@pytest.fixture(scope="session")
def unihan_ensure_quick(
    unihan_quick_path: pathlib.Path,
    unihan_quick_options: "UnihanOptions",
    unihan_quick_packager: "Packager",
) -> None:
    """Setup a tiny portion of UNIHAN, return a UnihanOptions.

    >>> import pathlib

    >>> from unihan_etl.core import Packager
    >>> from unihan_etl.options import Options as UnihanOptions

    >>> def test_unihan_ensure_quick(
    ...     unihan_quick_path: pathlib.Path,
    ...     unihan_quick_options: "UnihanOptions",
    ...     unihan_quick_packager: "Packager",
    ... ) -> None:
    ...     unihan_quick_destination = unihan_quick_options.destination
    ...     assert unihan_quick_destination.exists()
    ...     assert unihan_quick_destination.stat().st_size == 171_968
    ...
    ...     assert unihan_quick_options.work_dir.exists()
    ...     unihan_readings = unihan_quick_options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size == 21_631

    .. ::
        >>> locals().keys()
        dict_keys(...)

        >>> source = ''.join([e.source for e in request._pyfuncitem.dtest.examples][:4])
        >>> pytester = request.getfixturevalue('pytester')

        >>> pytester.makepyfile(**{'whatever.py': source})
        PosixPath(...)

        >>> result = pytester.runpytest('whatever.py', '--disable-warnings')
        ===...

        >>> result.assert_outcomes(passed=1)

    Extending fixtures:

    >>> import pathlib

    >>> import pytest

    >>> from unihan_etl.core import Packager
    >>> from unihan_etl.options import Options as UnihanOptions

    >>> @pytest.fixture
    ... def my_unihan(
    ...     unihan_quick_path: pathlib.Path,
    ...     unihan_quick_options: "UnihanOptions",
    ...     unihan_quick_packager: "Packager",
    ... ) -> "Packager":
    ...     return unihan_quick_packager

    >>> def test_my_extended_unihan_Fixture(my_unihan: "Packager") -> None:
    ...     my_unihan.download()
    ...     my_unihan_destination = my_unihan.options.destination
    ...     if not my_unihan_destination.exists():
    ...         my_unihan.export()
    ...     assert my_unihan_destination.exists()
    ...     assert my_unihan_destination.stat().st_size == 171_968
    ...
    ...     assert my_unihan.options.work_dir.exists()
    ...     unihan_readings = my_unihan.options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size == 21631

    .. ::
        >>> locals().keys()
        dict_keys(...)

        >>> source = ''.join(
        ...     [e.source for e in request._pyfuncitem.dtest.examples][10:16]
        ... )
        >>> pytester = request.getfixturevalue('pytester')

        >>> pytester.makepyfile(**{'example_2.py': source})
        PosixPath(...)

        >>> result = pytester.runpytest('example_2.py', '--disable-warnings')
        ===...

        >>> result.assert_outcomes(passed=1)
    """
    pkgr = Packager(unihan_quick_options)
    pkgr.download()

    if not pkgr.options.destination.exists():
        pkgr.export()

    return None


@pytest.fixture(scope="session")
def unihan_bootstrap_all(unihan_ensure_full: None, unihan_ensure_quick: None) -> None:
    """This should be used like so in your project's conftest.py:

    >>> import pytest
    >>> @pytest.fixture(scope="session", autouse=True)
    ... def bootstrap(unihan_bootstrap_all) -> None:
    ...     return None
    """
    return None


@pytest.fixture(scope="session")
def unihan_home_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Temporary `/home/` path."""
    return tmp_path_factory.mktemp("home")


@pytest.fixture(scope="session")
def unihan_home_user_name() -> str:
    """Default username to set for :func:`unihan_user_path` fixture."""
    return getpass.getuser()


@pytest.fixture(scope="session")
def unihan_user_path(
    unihan_home_path: pathlib.Path, unihan_home_user_name: str
) -> pathlib.Path:
    """Default temporary user directory.

    Used by: :func:`unihan_zshrc`

    Note: You will need to set the home directory, see :ref:`set_home`.
    """
    p = unihan_home_path / unihan_home_user_name
    p.mkdir()
    return p


@pytest.mark.skipif(not USING_ZSH, reason="Using ZSH")
@pytest.fixture(scope="session")
def unihan_zshrc(unihan_user_path: pathlib.Path) -> pathlib.Path:
    """This quiets ZSH default message.

    Needs a startup file .zshenv, .zprofile, .unihan_zshrc, .zlogin.
    """
    p = unihan_user_path / ".unihan_zshrc"
    p.touch()
    return p


if t.TYPE_CHECKING:
    from unihan_etl.types import (
        ColumnData,
        ExpandedExport,
        UntypedNormalizedData,
    )


@pytest.fixture
def unihan_test_options() -> t.Union[UnihanOptions, t.Mapping[str, t.Any]]:
    return UnihanOptions(input_files=["Unihan_Readings.txt"])


@pytest.fixture(scope="session")
def unihan_mock_zip_pathname() -> str:
    return "Unihan.zip"


@pytest.fixture(scope="session")
def unihan_quick_fixture_files() -> t.List[pathlib.Path]:
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
    return [QUICK_FIXTURE_PATH / f for f in files]


@pytest.fixture(scope="session")
def unihan_mock_test_dir(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    return tmp_path_factory.mktemp("unihan_etl")


@pytest.fixture(scope="session")
def unihan_mock_zip_path(
    unihan_mock_test_dir: pathlib.Path, unihan_mock_zip_pathname: str
) -> pathlib.Path:
    return unihan_mock_test_dir / unihan_mock_zip_pathname


@pytest.fixture(scope="session")
def unihan_mock_zip(
    unihan_mock_zip_path: pathlib.Path, unihan_quick_data: str
) -> zipfile.ZipFile:
    zf = zipfile.ZipFile(str(unihan_mock_zip_path), "a")
    zf.writestr("Unihan_Readings.txt", unihan_quick_data.encode("utf-8"))
    zf.close()
    return zf


@pytest.fixture(scope="session")
def unihan_quick_columns() -> "ColumnData":
    return (
        constants.CUSTOM_DELIMITED_FIELDS
        + constants.INDEX_FIELDS
        + constants.SPACE_DELIMITED_FIELDS
    )


@pytest.fixture(scope="session")
def unihan_quick_normalized_data(
    unihan_quick_columns: "ColumnData",
    unihan_quick_fixture_files: t.List[pathlib.Path],
) -> "UntypedNormalizedData":
    data = core.load_data(files=unihan_quick_fixture_files)

    return core.normalize(data, unihan_quick_columns)


@pytest.fixture(scope="session")
def unihan_quick_expanded_data(
    unihan_quick_normalized_data: t.List[t.Dict[str, t.Any]]
) -> "ExpandedExport":
    return core.expand_delimiters(unihan_quick_normalized_data)


@pytest.fixture(scope="session")
def unihan_quick_data() -> str:
    r"""Raw snippet excerpted from UNIHAN corpus.

    >>> def test_unihan_quick_data(
    ...     unihan_quick_data: str,
    ... ) -> None:
    ...     assert isinstance(unihan_quick_data, str)
    ...
    ...     assert isinstance(unihan_quick_data.splitlines()[1], str)
    ...

    .. ::
        >>> locals().keys()
        dict_keys(...)

        >>> source = ''.join([e.source for e in request._pyfuncitem.dtest.examples][:1])
        >>> pytester = request.getfixturevalue('pytester')

        >>> pytester.makepyfile(
        ...     **{'test_pytest_plugin__unihan_quick_data.py': source}
        ... )
        PosixPath(...)

        >>> result = pytester.runpytest(
        ...     'test_pytest_plugin__unihan_quick_data.py', '--disable-warnings'
        ... )
        ===...

        >>> result.assert_outcomes(passed=1)
    """
    return """\
U+3400	kCantonese	jau1
U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
U+3400	kMandarin	qiū
U+3401	kCantonese	tim2
U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
U+3401	kHanyuPinyin	10019.020:tiàn
"""
