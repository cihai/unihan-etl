"""pytest plugin for unihan-etl."""

from __future__ import annotations

import contextlib
import getpass
import logging
import os
import pathlib
import shutil
import typing as t
import zipfile
import zlib
from collections.abc import Generator, Mapping

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


def _cache_lock(
    config: pytest.Config,
    basetemp: pathlib.Path,
) -> contextlib.AbstractContextManager[t.Any]:
    """Return a context manager serializing shared ``.unihan_cache`` writes.

    Off xdist (no ``workerinput`` on the config) this is a no-op
    :func:`contextlib.nullcontext`. Under an xdist worker it is an inter-process
    :class:`filelock.FileLock` on the shared base temp dir, so concurrent workers
    build the cache one at a time. ``filelock`` is imported lazily here so the
    plugin still loads for downstream consumers that do not depend on it.
    """
    if not hasattr(config, "workerinput"):
        return contextlib.nullcontext()
    try:
        from filelock import FileLock
    except ModuleNotFoundError as exc:  # pragma: no cover - optional test extra
        msg = "filelock is required to run these fixtures under pytest-xdist"
        raise ModuleNotFoundError(msg) from exc

    return FileLock(str(basetemp / "unihan_cache.lock"))


@pytest.fixture(scope="session")
def unihan_cache_lock(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> contextlib.AbstractContextManager[t.Any]:
    """Serialize shared ``.unihan_cache`` writes across xdist workers.

    A no-op in single-process runs; under xdist it locks on the shared base temp
    so only one worker (re)builds the cache while the others wait and reuse it.
    One lock deliberately covers both the quick and full datasets: a session
    bootstraps both, so per-dataset locks would not reduce contention.
    """
    return _cache_lock(request.config, tmp_path_factory.getbasetemp().parent)


@pytest.fixture(scope="session")
def unihan_user_cache_path() -> pathlib.Path:
    """unihan-etl cache directory, overridable."""
    return app_dirs.user_cache_dir


@pytest.fixture(scope="session")
def unihan_project_cache_path() -> pathlib.Path:
    """Return unihan_etl project-based cache path. Override to path of your choice."""
    return PROJECT_PATH / ".unihan_cache"


@pytest.fixture(scope="session")
def unihan_cache_path(unihan_project_cache_path: pathlib.Path) -> pathlib.Path:
    """Return unihan_etl cache path, override this to destination of your choice."""
    return unihan_project_cache_path


@pytest.fixture(scope="session")
def unihan_fixture_root(unihan_cache_path: pathlib.Path) -> pathlib.Path:
    """Return pytest cached directory fixture root."""
    return unihan_cache_path / "f"


@pytest.fixture(scope="session")
def unihan_full_path(unihan_fixture_root: pathlib.Path) -> pathlib.Path:
    """Return directory path for "full" UNIHAN dataset."""
    return unihan_fixture_root / "full"


@pytest.fixture(scope="session")
def unihan_full_options(unihan_full_path: pathlib.Path) -> UnihanOptions:
    """Return UnihanOptions for "full" UNIHAN dataset."""
    return UnihanOptions(
        work_dir=unihan_full_path / "work",
        zip_path=unihan_full_path / "downloads" / "Unihan.zip",
        destination=unihan_full_path / "out" / "unihan.csv",
    )


@pytest.fixture(scope="session")
def unihan_full_packager(
    unihan_full_path: pathlib.Path,
    unihan_full_options: UnihanOptions,
) -> Packager:
    """Return Packager for "full" portion of UNIHAN, return a UnihanOptions."""
    return Packager(unihan_full_options)


@pytest.fixture(scope="session")
def unihan_ensure_full(
    unihan_full_path: pathlib.Path,
    unihan_full_options: UnihanOptions,
    unihan_full_packager: Packager,
    unihan_cache_lock: contextlib.AbstractContextManager[t.Any],
) -> None:
    """Download and extract "full" UNIHAN, return UnihanOptions.

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
    ...     assert unihan_readings.stat().st_size > 6_200_000

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
    ...     assert unihan_readings.stat().st_size > 6_200_000

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
    with unihan_cache_lock:
        pkgr.download()
        if not pkgr.options.destination.exists():
            pkgr.export()


@pytest.fixture(scope="session")
def unihan_quick_path(unihan_fixture_root: pathlib.Path) -> pathlib.Path:
    """Return directory path for "quick" test data set."""
    return unihan_fixture_root / "quick"


@pytest.fixture(scope="session")
def unihan_quick_zip_path(unihan_quick_path: pathlib.Path) -> pathlib.Path:
    """Return zip file path for "quick" test data set."""
    return unihan_quick_path / "downloads" / "Unihan.zip"


@pytest.fixture(scope="session")
def unihan_quick_work_path(unihan_quick_path: pathlib.Path) -> pathlib.Path:
    """Return the "quick" dataset extraction (work) directory."""
    return unihan_quick_path / "work"


@pytest.fixture(scope="session")
def unihan_quick_out_path(unihan_quick_path: pathlib.Path) -> pathlib.Path:
    """Return the "quick" dataset export (out) directory."""
    return unihan_quick_path / "out"


def _quick_zip_is_stale(
    zip_path: pathlib.Path,
    source_files: list[pathlib.Path],
) -> bool:
    """Return True if the cached quick zip is missing, invalid, or out of date.

    Staleness is bidirectional and content-aware: the cache is stale when the
    archive is missing or not a valid zip, when its member set differs from the
    source set (a file added or removed), or when any source file's content
    differs from the archived member by CRC32. zipfile stores a CRC per member,
    so no sidecar hash file is needed.
    """
    if not zip_path.is_file() or not zipfile.is_zipfile(zip_path):
        return True
    with zipfile.ZipFile(zip_path) as zf:
        if set(zf.namelist()) != {source.name for source in source_files}:
            return True
        for source in source_files:
            archived_crc = zf.getinfo(source.name).CRC
            if archived_crc != zlib.crc32(source.read_bytes()) & 0xFFFFFFFF:
                return True
    return False


def _sync_quick_zip(
    zip_path: pathlib.Path,
    source_files: list[pathlib.Path],
) -> bool:
    """Build or refresh the quick-dataset zip; return True if it was (re)built.

    Rewrites the whole archive whenever it is stale -- append mode cannot replace
    or drop a member. The archive is written to a sibling temp file and atomically
    moved into place, so a reader never observes a half-written zip. Returns False
    when the cache is already current, so callers can skip invalidating derived
    artifacts.
    """
    if not _quick_zip_is_stale(zip_path, source_files):
        return False
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = zip_path.parent / (zip_path.name + ".tmp")
    with zipfile.ZipFile(tmp_path, "w") as zf:
        for source in source_files:
            zf.write(source, source.name)
    tmp_path.replace(zip_path)
    return True


def _sync_quick_dataset(
    zip_path: pathlib.Path,
    source_files: list[pathlib.Path],
    work_dir: pathlib.Path,
    out_dir: pathlib.Path,
) -> bool:
    """Sync the quick zip and, on a rebuild, drop the derived work/out layers.

    Returns True when the zip was rebuilt (and the derived directories cleared so
    extraction and export regenerate), False when the cache was already current.
    """
    rebuilt = _sync_quick_zip(zip_path, source_files)
    if rebuilt:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(out_dir, ignore_errors=True)
    return rebuilt


@pytest.fixture(scope="session")
def unihan_quick_zip(
    unihan_quick_zip_path: pathlib.Path,
    unihan_quick_fixture_files: list[pathlib.Path],
    unihan_quick_work_path: pathlib.Path,
    unihan_quick_out_path: pathlib.Path,
    unihan_cache_lock: contextlib.AbstractContextManager[t.Any],
) -> Generator[zipfile.ZipFile, None, None]:
    """Yield the "quick" test data set zip, rebuilding it when sources change.

    The cached archive is refreshed (by CRC32) whenever a bundled quick source
    file changes, so edits propagate without manually clearing ``.unihan_cache``.
    On a rebuild the derived ``work/`` and ``out/`` artifacts are cleared so
    :class:`~unihan_etl.core.Packager` re-extracts and re-exports. The yielded
    handle is open for reading and closed on teardown.

    Teardown
    --------
    Closes the yielded archive handle.
    """
    # work/ and out/ are the same fixtures unihan_quick_options uses, so the
    # cleared dirs always match the extraction/export targets. Cleared on a
    # rebuild so extract/export regenerate from the refreshed archive.
    with unihan_cache_lock:
        _sync_quick_dataset(
            unihan_quick_zip_path,
            unihan_quick_fixture_files,
            unihan_quick_work_path,
            unihan_quick_out_path,
        )

    with zipfile.ZipFile(unihan_quick_zip_path) as zf:
        yield zf


@pytest.fixture(scope="session")
def unihan_quick_options(
    unihan_quick_zip: zipfile.ZipFile,
    unihan_quick_zip_path: pathlib.Path,
    unihan_quick_work_path: pathlib.Path,
    unihan_quick_out_path: pathlib.Path,
) -> UnihanOptions:
    """Return UnihanOptions for "quick" test data set."""
    return UnihanOptions(
        work_dir=unihan_quick_work_path,
        zip_path=unihan_quick_zip_path,
        destination=unihan_quick_out_path / "unihan.csv",
    )


@pytest.fixture(scope="session")
def unihan_quick_packager(
    unihan_quick_path: pathlib.Path,
    unihan_quick_options: UnihanOptions,
) -> Packager:
    """Bootstrap a small, but effective portion of UNIHAN, return a UnihanOptions."""
    return Packager(unihan_quick_options)


@pytest.fixture(scope="session")
def unihan_ensure_quick(
    unihan_quick_path: pathlib.Path,
    unihan_quick_options: UnihanOptions,
    unihan_quick_packager: Packager,
    unihan_cache_lock: contextlib.AbstractContextManager[t.Any],
) -> None:
    """Return a small, but effective portion of UNIHAN, return a UnihanOptions.

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
    ...     assert unihan_quick_destination.stat().st_size >= 140_000
    ...     assert unihan_quick_destination.stat().st_size < 200_000
    ...
    ...     assert unihan_quick_options.work_dir.exists()
    ...     unihan_readings = unihan_quick_options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size >= 21_631
    ...     assert unihan_readings.stat().st_size < 30_000

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
    ...     assert my_unihan_destination.stat().st_size >= 140_000
    ...     assert my_unihan_destination.stat().st_size < 200_000
    ...
    ...     assert my_unihan.options.work_dir.exists()
    ...     unihan_readings = my_unihan.options.work_dir / 'Unihan_Readings.txt'
    ...     assert unihan_readings.stat().st_size >= 21_000
    ...     assert unihan_readings.stat().st_size < 30_000

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
    with unihan_cache_lock:
        pkgr.download()
        if not pkgr.options.destination.exists():
            pkgr.export()


@pytest.fixture(scope="session")
def unihan_bootstrap_all(unihan_ensure_full: None, unihan_ensure_quick: None) -> None:
    """Noop that bootstraps all unihan_etl pytest datasets ("full" and "quick").

    This should be used like so in your project's conftest.py:

    >>> import pytest
    >>> @pytest.fixture(scope="session", autouse=True)
    ... def bootstrap(unihan_bootstrap_all) -> None:
    ...     return None
    """
    return


@pytest.fixture(scope="session")
def unihan_home_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """Return temporary `/home/` path for use by unihan_etl pytest fixtures."""
    return tmp_path_factory.mktemp("home")


@pytest.fixture(scope="session")
def unihan_home_user_name() -> str:
    """Return username to set for :func:`unihan_user_path` fixture."""
    return getpass.getuser()


@pytest.fixture(scope="session")
def unihan_user_path(
    unihan_home_path: pathlib.Path,
    unihan_home_user_name: str,
) -> pathlib.Path:
    """Return temporary user directory.

    Used by: :func:`unihan_zshrc`

    Note: You will need to set the home directory, see :ref:`set_home`.
    """
    p = unihan_home_path / unihan_home_user_name
    p.mkdir()
    return p


@pytest.fixture(scope="session")
def unihan_zshrc(unihan_user_path: pathlib.Path) -> pathlib.Path:
    """Suppress ZSH default message.

    Needs a startup file .zshenv, .zprofile, .unihan_zshrc, .zlogin.
    """
    p = unihan_user_path / ".unihan_zshrc"
    p.touch()
    return p


if t.TYPE_CHECKING:
    from typing import TypeAlias

    from unihan_etl.types import (
        ColumnData,
        ExpandedExport,
        UntypedNormalizedData,
    )

UnihanTestOptions: TypeAlias = UnihanOptions | Mapping[str, t.Any]
"""Options accepted by :fixture:`unihan_test_options`.

Either a fully-configured :class:`~unihan_etl.options.Options` dataclass or a
plain mapping of keyword arguments.
"""


@pytest.fixture
def unihan_test_options() -> UnihanTestOptions:
    """Return UnihanOptions for test data."""
    return UnihanOptions(input_files=["Unihan_Readings.txt"])


@pytest.fixture(scope="session")
def unihan_mock_zip_pathname() -> str:
    """Return zip file name in "quick" test data set."""
    return "Unihan.zip"


@pytest.fixture(scope="session")
def unihan_quick_fixture_files() -> list[pathlib.Path]:
    """Return files used in "quick" test data set."""
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
    """Return temporary directory for unihan_etl py.test fixtures."""
    return tmp_path_factory.mktemp("unihan_etl")


@pytest.fixture(scope="session")
def unihan_mock_zip_path(
    unihan_mock_test_dir: pathlib.Path,
    unihan_mock_zip_pathname: str,
) -> pathlib.Path:
    """Return path to Unihan zipfile."""
    return unihan_mock_test_dir / unihan_mock_zip_pathname


@pytest.fixture(scope="session")
def unihan_mock_zip(
    unihan_mock_zip_path: pathlib.Path,
    unihan_quick_data: str,
) -> Generator[zipfile.ZipFile, None, None]:
    """Yield a mock Unihan zipfile, open for reading and closed on teardown.

    Teardown
    --------
    Closes the yielded archive handle.
    """
    with zipfile.ZipFile(str(unihan_mock_zip_path), "a") as zf:
        if "Unihan_Readings.txt" not in zf.namelist():
            zf.writestr("Unihan_Readings.txt", unihan_quick_data.encode("utf-8"))
    with zipfile.ZipFile(str(unihan_mock_zip_path)) as zf:
        yield zf


@pytest.fixture(scope="session")
def unihan_quick_columns() -> ColumnData:
    """Return columns used in "quick" test data set."""
    return (
        constants.CUSTOM_DELIMITED_FIELDS
        + constants.INDEX_FIELDS
        + constants.SPACE_DELIMITED_FIELDS
    )


@pytest.fixture(scope="session")
def unihan_quick_normalized_data(
    unihan_quick_columns: ColumnData,
    unihan_quick_fixture_files: list[pathlib.Path],
) -> UntypedNormalizedData:
    """Return normalized test data from "quick" test data set."""
    data = core.load_data(files=unihan_quick_fixture_files)

    return core.normalize(data, unihan_quick_columns)


@pytest.fixture(scope="session")
def unihan_quick_expanded_data(
    unihan_quick_normalized_data: list[dict[str, t.Any]],
) -> ExpandedExport:
    """Return a list of expanded fields from "quick" test data."""
    return core.expand_delimiters(unihan_quick_normalized_data)


@pytest.fixture(scope="session")
def unihan_quick_data() -> str:
    r"""Raw snippet excerpted from UNIHAN corpus from "quick" test data.

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
