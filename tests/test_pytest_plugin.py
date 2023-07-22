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
        test_id="ensure_full_unihan",
        files={
            "example.py": textwrap.dedent(
                """
import pathlib

from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

def test_ensure_full_unihan(
    full_unihan_path: pathlib.Path,
    full_unihan_options: "UnihanOptions",
    full_unihan_packager: "Packager",
) -> None:
    assert full_unihan_path is not None
    assert full_unihan_options is not None
    assert full_unihan_packager is not None

    assert isinstance(full_unihan_path, pathlib.Path)
    assert isinstance(full_unihan_options, UnihanOptions)
    assert isinstance(full_unihan_packager, Packager)

    assert full_unihan_path.exists()

    full_unihan_destination = full_unihan_options.destination
    assert full_unihan_destination.exists()
    assert full_unihan_destination.stat().st_size > 20_000_000

    assert full_unihan_options.work_dir.exists()
    unihan_readings = full_unihan_options.work_dir / 'Unihan_Readings.txt'
    assert unihan_readings.stat().st_size > 6200000
        """
            )
        },
        tests_passed=1,
    ),
    PytestPluginFixture(
        test_id="ensure_quick_unihan",
        files={
            "example.py": textwrap.dedent(
                """
import pathlib

from unihan_etl.core import Packager
from unihan_etl.options import Options as UnihanOptions

def test_ensure_quick_unihan(
    quick_unihan_path: pathlib.Path,
    quick_unihan_options: "UnihanOptions",
    quick_unihan_packager: "Packager",
) -> None:
    assert quick_unihan_path is not None
    assert quick_unihan_options is not None
    assert quick_unihan_packager is not None

    assert isinstance(quick_unihan_path, pathlib.Path)
    assert isinstance(quick_unihan_options, UnihanOptions)
    assert isinstance(quick_unihan_packager, Packager)

    assert quick_unihan_path.exists()

    quick_unihan_destination = quick_unihan_options.destination
    assert quick_unihan_destination.exists()
    assert quick_unihan_destination.stat().st_size == 171968

    assert quick_unihan_options.work_dir.exists()
    unihan_readings = quick_unihan_options.work_dir / 'Unihan_Readings.txt'
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
