"""Conftest.py (root-level).

We keep this in root pytest fixtures in pytest's doctest plugin to be available, as well
as avoiding conftest.py from being included in the wheel, in addition to pytest_plugin
for pytester only being available via the root directory.

See "pytest_plugins in non-top-level conftest files" in
https://docs.pytest.org/en/stable/deprecations.html
"""
import pathlib
import shutil
import typing as t

import pytest
from _pytest.doctest import DoctestItem

from unihan_etl.pytest_plugin import USING_ZSH

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def add_doctest_fixtures(
    request: pytest.FixtureRequest,
    doctest_namespace: t.Dict[str, t.Any],
) -> None:
    """Harness pytest fixtures to doctest namespace."""
    if isinstance(request._pyfuncitem, DoctestItem) and shutil.which("tmux"):
        request.getfixturevalue("set_home")
        doctest_namespace["request"] = request


@pytest.fixture(autouse=True, scope="function")
def set_home(
    monkeypatch: pytest.MonkeyPatch,
    unihan_user_path: pathlib.Path,
) -> None:
    """Set home directory for pytest tests."""
    monkeypatch.setenv("HOME", str(unihan_user_path))


@pytest.fixture(autouse=True, scope="session")
def setup(
    request: pytest.FixtureRequest,
    unihan_ensure_quick: None,
    unihan_ensure_full: None,
) -> None:
    """Configure test fixtures for pytest."""
    if USING_ZSH:
        request.getfixturevalue("unihan_zshrc")
