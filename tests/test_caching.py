"""Tests for unihan-etl caching: zip staleness invalidation and extract gating."""

from __future__ import annotations

import dataclasses
import os
import pathlib
import shutil
import typing as t
import zipfile

import pytest

from unihan_etl import core
from unihan_etl.core import Packager
from unihan_etl.pytest_plugin import _sync_quick_dataset, _sync_quick_zip

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from http.client import HTTPMessage
    from urllib.request import _DataType

    from unihan_etl.options import Options
    from unihan_etl.types import StrPath


class StaleZipCase(t.NamedTuple):
    """Case for :func:`test_quick_zip_staleness_rebuild`."""

    test_id: str
    mutate: str  # "edit" | "none" | "add" | "remove" | "corrupt"
    expect_rebuilt: bool


STALE_ZIP_CASES: list[StaleZipCase] = [
    StaleZipCase(test_id="edited_source_rebuilds", mutate="edit", expect_rebuilt=True),
    StaleZipCase(test_id="unchanged_source_skips", mutate="none", expect_rebuilt=False),
    StaleZipCase(test_id="added_source_rebuilds", mutate="add", expect_rebuilt=True),
    StaleZipCase(
        test_id="removed_source_rebuilds", mutate="remove", expect_rebuilt=True
    ),
    StaleZipCase(
        test_id="corrupt_archive_rebuilds", mutate="corrupt", expect_rebuilt=True
    ),
]


@pytest.mark.parametrize(
    StaleZipCase._fields,
    STALE_ZIP_CASES,
    ids=[c.test_id for c in STALE_ZIP_CASES],
)
def test_quick_zip_staleness_rebuild(
    test_id: str,
    mutate: str,
    expect_rebuilt: bool,
    tmp_path: pathlib.Path,
) -> None:
    """_sync_quick_zip rebuilds the cached zip when the source set changes.

    Staleness is bidirectional and content-aware (CRC32 per member): an edit, an
    added source, a removed source, or a missing/corrupt archive triggers a
    rebuild, while an unchanged source set is left untouched.
    """
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    readings = src_dir / "Unihan_Readings.txt"
    readings.write_text("U+3400\tkCantonese\tjau1\n", encoding="utf-8")
    variants = src_dir / "Unihan_Variants.txt"
    variants.write_text("U+346E\tkSemanticVariant\tU+34CE\n", encoding="utf-8")
    sources = [readings, variants]
    zip_path = tmp_path / "downloads" / "Unihan.zip"

    # Initial build always counts as a (re)build from an absent archive.
    assert _sync_quick_zip(zip_path, sources) is True
    with zipfile.ZipFile(zip_path) as zf:
        assert set(zf.namelist()) == {"Unihan_Readings.txt", "Unihan_Variants.txt"}

    if mutate == "edit":
        readings.write_text("U+3401\tkCantonese\ttim2\n", encoding="utf-8")
    elif mutate == "add":
        numeric = src_dir / "Unihan_NumericValues.txt"
        numeric.write_text("U+3405\tkOtherNumeric\t5\n", encoding="utf-8")
        sources = [readings, variants, numeric]
    elif mutate == "remove":
        sources = [readings]
    elif mutate == "corrupt":
        zip_path.write_bytes(b"not a zip")

    assert _sync_quick_zip(zip_path, sources) is expect_rebuilt

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        if mutate == "edit":
            assert zf.read("Unihan_Readings.txt").decode("utf-8").startswith("U+3401")
        elif mutate == "add":
            assert "Unihan_NumericValues.txt" in names
        elif mutate == "remove":
            assert names == {"Unihan_Readings.txt"}
        elif mutate == "corrupt":
            assert "Unihan_Readings.txt" in names
        else:
            assert names == {"Unihan_Readings.txt", "Unihan_Variants.txt"}


def test_sync_quick_dataset_clears_derived_on_rebuild(tmp_path: pathlib.Path) -> None:
    """A rebuild drops the derived work/ and out/ layers; a no-op leaves them."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    readings = src_dir / "Unihan_Readings.txt"
    readings.write_text("U+3400\tkCantonese\tjau1\n", encoding="utf-8")
    sources = [readings]
    zip_path = tmp_path / "downloads" / "Unihan.zip"
    work_dir = tmp_path / "work"
    out_dir = tmp_path / "out"

    def seed_derived() -> tuple[pathlib.Path, pathlib.Path]:
        work_dir.mkdir(exist_ok=True)
        out_dir.mkdir(exist_ok=True)
        work_file = work_dir / "Unihan_Readings.txt"
        out_file = out_dir / "unihan.csv"
        work_file.write_text("SENTINEL\n", encoding="utf-8")
        out_file.write_text("SENTINEL\n", encoding="utf-8")
        return work_file, out_file

    # Initial build is a rebuild -> derived layers are cleared.
    work_file, out_file = seed_derived()
    assert _sync_quick_dataset(zip_path, sources, work_dir, out_dir) is True
    assert not work_file.exists()
    assert not out_file.exists()

    # Unchanged sources -> no rebuild -> freshly seeded derived layers survive.
    work_file, out_file = seed_derived()
    assert _sync_quick_dataset(zip_path, sources, work_dir, out_dir) is False
    assert work_file.read_text(encoding="utf-8") == "SENTINEL\n"
    assert out_file.read_text(encoding="utf-8") == "SENTINEL\n"


class PackagerExtractCase(t.NamedTuple):
    """Case for :func:`test_packager_download_extract_gate`."""

    test_id: str
    prepopulate: bool  # work_dir already holds the input file (a sentinel)
    cache: bool
    expect_overwrite: bool  # extraction overwrites the sentinel


PACKAGER_EXTRACT_CASES: list[PackagerExtractCase] = [
    PackagerExtractCase(
        test_id="extracts_when_work_empty",
        prepopulate=False,
        cache=True,
        expect_overwrite=True,
    ),
    PackagerExtractCase(
        test_id="skips_extract_when_present_and_cached",
        prepopulate=True,
        cache=True,
        expect_overwrite=False,
    ),
    PackagerExtractCase(
        test_id="reextracts_when_cache_disabled",
        prepopulate=True,
        cache=False,
        expect_overwrite=True,
    ),
]


@pytest.mark.parametrize(
    PackagerExtractCase._fields,
    PACKAGER_EXTRACT_CASES,
    ids=[c.test_id for c in PACKAGER_EXTRACT_CASES],
)
def test_packager_download_extract_gate(
    test_id: str,
    prepopulate: bool,
    cache: bool,
    expect_overwrite: bool,
    tmp_path: pathlib.Path,
    unihan_mock_zip: zipfile.ZipFile,
    unihan_mock_zip_path: pathlib.Path,
    unihan_test_options: Options,
) -> None:
    """Packager.download extracts only when work_dir lacks inputs or cache is off.

    Guards the gate the quick-zip invalidation relies on: clearing work/ forces a
    re-extract on the next session run.
    """
    sentinel = "SENTINEL\n"
    zip_path = tmp_path / "downloads" / "Unihan.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(str(unihan_mock_zip_path), str(zip_path))
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    work_file = work_dir / "Unihan_Readings.txt"
    if prepopulate:
        work_file.write_text(sentinel, encoding="utf-8")

    download_calls = 0

    def urlretrieve(
        url: str,
        filename: StrPath | None = None,
        reporthook: Callable[[int, int, int], object] | None = None,
        data: _DataType | None = None,
    ) -> tuple[str, HTTPMessage]:
        nonlocal download_calls
        download_calls += 1
        shutil.copy(str(unihan_mock_zip_path), str(zip_path))
        from http.client import HTTPMessage as _HTTPMessage

        return ("", _HTTPMessage())

    packager = Packager(
        dataclasses.replace(
            unihan_test_options,
            source="https://example.invalid/Unihan.zip",
            zip_path=zip_path,
            work_dir=work_dir,
            cache=cache,
        ),
    )
    packager.download(urlretrieve_fn=urlretrieve)

    assert download_calls == (0 if cache else 1)
    assert work_file.exists()
    if expect_overwrite:
        assert work_file.read_text(encoding="utf-8") != sentinel
    else:
        assert work_file.read_text(encoding="utf-8") == sentinel


def test_mock_zip_fixture_is_open(unihan_mock_zip: zipfile.ZipFile) -> None:
    """The unihan_mock_zip fixture yields an open, readable archive handle.

    A closed handle raises ``ValueError`` on ``read()``; an open one returns the
    member bytes.
    """
    assert "Unihan_Readings.txt" in unihan_mock_zip.namelist()
    assert unihan_mock_zip.read("Unihan_Readings.txt")


def test_has_valid_zip_memoizes_integrity_check(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    unihan_mock_zip: zipfile.ZipFile,
    unihan_mock_zip_path: pathlib.Path,
) -> None:
    """has_valid_zip runs the deep member-CRC check once per file state.

    Repeat checks of an unchanged archive hit the memo (no re-decompress);
    rewriting the file (new mtime/size) invalidates it and re-verifies.
    """
    core._zip_integrity_ok.cache_clear()
    zip_path = tmp_path / "Unihan.zip"
    shutil.copy(str(unihan_mock_zip_path), str(zip_path))

    testzip_calls = 0
    real_testzip = zipfile.ZipFile.testzip

    def counting_testzip(self: zipfile.ZipFile) -> str | None:
        nonlocal testzip_calls
        testzip_calls += 1
        return real_testzip(self)

    monkeypatch.setattr(zipfile.ZipFile, "testzip", counting_testzip)

    assert core.has_valid_zip(zip_path)
    assert core.has_valid_zip(zip_path)
    assert core.has_valid_zip(zip_path)
    assert testzip_calls == 1  # deep check ran once, then memoized

    # A rewrite changes the (mtime, size) fingerprint -> the memo re-verifies.
    st = zip_path.stat()
    os.utime(zip_path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    assert core.has_valid_zip(zip_path)
    assert testzip_calls == 2
