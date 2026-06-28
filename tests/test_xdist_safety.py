"""Tests for xdist-safe shared-cache locking in the pytest plugin."""

from __future__ import annotations

import contextlib
import multiprocessing
import pathlib
import types
import typing as t
import zipfile

import pytest
from filelock import FileLock

from unihan_etl.pytest_plugin import _cache_lock, _sync_quick_dataset


class CacheLockCase(t.NamedTuple):
    """Case for :func:`test_cache_lock_selection`."""

    test_id: str
    under_xdist: bool
    expect_filelock: bool


CACHE_LOCK_CASES: list[CacheLockCase] = [
    CacheLockCase(
        test_id="off_xdist_nullcontext", under_xdist=False, expect_filelock=False
    ),
    CacheLockCase(
        test_id="under_xdist_filelock", under_xdist=True, expect_filelock=True
    ),
]


@pytest.mark.parametrize(
    CacheLockCase._fields,
    CACHE_LOCK_CASES,
    ids=[c.test_id for c in CACHE_LOCK_CASES],
)
def test_cache_lock_selection(
    test_id: str,
    under_xdist: bool,
    expect_filelock: bool,
    tmp_path: pathlib.Path,
) -> None:
    """_cache_lock is a no-op off xdist and a FileLock under an xdist worker.

    Off xdist it must return a plain nullcontext (the downstream-safe path that
    never touches filelock); only an actual worker, signalled by ``workerinput``
    on the config, gets an inter-process lock.
    """
    config_ns = types.SimpleNamespace()
    if under_xdist:
        config_ns.workerinput = {}
    config = t.cast("pytest.Config", config_ns)

    lock = _cache_lock(config, tmp_path)

    if expect_filelock:
        assert isinstance(lock, FileLock)
    else:
        assert isinstance(lock, contextlib.nullcontext)
    with lock:  # usable as a context manager either way
        pass


def _build_quick_cache(payload: tuple[t.Any, ...]) -> bool:
    """Worker: build the quick cache while holding the shared inter-process lock.

    Mirrors the locked region the quick fixtures run
    (``with unihan_cache_lock: _sync_quick_dataset(...)``).
    """
    zip_path, sources, work_dir, out_dir, lock_path = payload
    with FileLock(str(lock_path)):
        return _sync_quick_dataset(zip_path, sources, work_dir, out_dir)


def test_concurrent_cache_build_serializes(tmp_path: pathlib.Path) -> None:
    """Two processes building the shared cache under the lock do not race.

    Exercises the same locked region the quick fixtures use, across real OS
    processes: the inter-process ``FileLock`` serializes them, so the archive is
    built exactly once and stays valid. Cheaper and more deterministic than a
    nested ``pytest-xdist`` run, and it never touches the real ``.unihan_cache``.
    """
    src = tmp_path / "src"
    src.mkdir()
    readings = src / "Unihan_Readings.txt"
    readings.write_text("U+3400\tkCantonese\tjau1\n", encoding="utf-8")
    cache = tmp_path / "cache"
    payload = (
        cache / "downloads" / "Unihan.zip",
        [readings],
        cache / "work",
        cache / "out",
        tmp_path / "unihan_cache.lock",
    )

    with multiprocessing.Pool(2) as pool:
        results = pool.map(_build_quick_cache, [payload, payload])

    assert sum(bool(r) for r in results) == 1  # built once, not twice
    assert zipfile.is_zipfile(payload[0])
