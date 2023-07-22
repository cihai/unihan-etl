import textwrap
import typing as t

import pytest

FixtureFileDict = t.Dict[str, str]


class PytestPluginFixture(t.NamedTuple):
    # pytest
    test_id: str

    # Content
    files: FixtureFileDict
    tests_passed: int


FIXTURES = [
    PytestPluginFixture(
        test_id="unihan_ensure_full",
        files={
            "example.py": textwrap.dedent(
                """
import pathlib

from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

def test_unihan_ensure_full(
    unihan_full_path: pathlib.Path,
    unihan_full_options: "UnihanOptions",
    unihan_full_packager: "Packager",
) -> None:
    assert unihan_full_path is not None
    assert unihan_full_options is not None
    assert unihan_full_packager is not None

    assert isinstance(unihan_full_path, pathlib.Path)
    assert isinstance(unihan_full_options, UnihanOptions)
    assert isinstance(unihan_full_packager, Packager)

    assert unihan_full_path.exists()

    unihan_full_destination = unihan_full_options.destination
    assert unihan_full_destination.exists()
    assert unihan_full_destination.stat().st_size > 20_000_000

    assert unihan_full_options.work_dir.exists()
    unihan_readings = unihan_full_options.work_dir / 'Unihan_Readings.txt'
    assert unihan_readings.stat().st_size > 6200000
        """
            )
        },
        tests_passed=1,
    ),
    PytestPluginFixture(
        test_id="ensure_unihan_quick",
        files={
            "example.py": textwrap.dedent(
                """
import pathlib

from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

def test_ensure_unihan_quick(
    unihan_quick_path: pathlib.Path,
    unihan_quick_options: "UnihanOptions",
    unihan_quick_packager: "Packager",
) -> None:
    assert unihan_quick_path is not None
    assert unihan_quick_options is not None
    assert unihan_quick_packager is not None

    assert isinstance(unihan_quick_path, pathlib.Path)
    assert isinstance(unihan_quick_options, UnihanOptions)
    assert isinstance(unihan_quick_packager, Packager)

    assert unihan_quick_path.exists()

    unihan_quick_destination = unihan_quick_options.destination
    assert unihan_quick_destination.exists()
    assert unihan_quick_destination.stat().st_size == 171968

    assert unihan_quick_options.work_dir.exists()
    unihan_readings = unihan_quick_options.work_dir / 'Unihan_Readings.txt'
    assert unihan_readings.stat().st_size == 21631
        """
            )
        },
        tests_passed=1,
    ),
]


@pytest.mark.parametrize(
    PytestPluginFixture._fields, FIXTURES, ids=[f.test_id for f in FIXTURES]
)
def test_plugin(
    pytester: pytest.Pytester,
    monkeypatch: pytest.MonkeyPatch,
    test_id: str,
    files: FixtureFileDict,
    tests_passed: int,
) -> None:
    # Initialize variables
    pytester.plugins = ["pytest_plugin"]
    pytester.makefile(
        ".ini",
        pytest=textwrap.dedent(
            """
[pytest]
addopts=-vv
        """.strip()
        ),
    )
    pytester.makeconftest(
        textwrap.dedent(
            r"""
import pathlib
import pytest

@pytest.fixture(autouse=True)
def setup(
    request: pytest.FixtureRequest,
) -> None:
    pass
    """
        )
    )
    tests_path = pytester.path / "tests"
    first_test_key = next(iter(files.keys()))
    first_test_filename = str(tests_path / first_test_key)

    # Setup Files
    tests_path.mkdir()
    for file_name, text in files.items():
        file = tests_path / file_name
        file.write_text(
            text,
            encoding="utf-8",
        )
    first_test_key = next(iter(files.keys()))
    first_test_filename = str(tests_path / first_test_key)

    # Test
    result = pytester.runpytest(str(first_test_filename))
    result.assert_outcomes(passed=1)
