"""Tests for PrivatePath utility."""

from __future__ import annotations

import pathlib
import typing as t

import pytest

from unihan_etl._internal.private_path import PrivatePath, collapse_home_in_string


class PrivatePathStrFixture(t.NamedTuple):
    """Test fixture for PrivatePath string representation."""

    test_id: str
    path_suffix: str  # Suffix to add to home, or absolute path if starts with /
    expected_output: str  # Use {HOME} for home path, ~ for collapsed


PRIVATE_PATH_STR_FIXTURES: list[PrivatePathStrFixture] = [
    PrivatePathStrFixture(
        test_id="home_collapsed_to_tilde",
        path_suffix="",
        expected_output="~",
    ),
    PrivatePathStrFixture(
        test_id="home_subdir_collapsed",
        path_suffix="/projects/unihan-etl",
        expected_output="~/projects/unihan-etl",
    ),
    PrivatePathStrFixture(
        test_id="config_dir_collapsed",
        path_suffix="/.config/unihan-etl",
        expected_output="~/.config/unihan-etl",
    ),
    PrivatePathStrFixture(
        test_id="tmp_not_collapsed",
        path_suffix="/tmp/test",
        expected_output="/tmp/test",
    ),
    PrivatePathStrFixture(
        test_id="usr_not_collapsed",
        path_suffix="/usr/local/bin",
        expected_output="/usr/local/bin",
    ),
]


@pytest.mark.parametrize(
    PrivatePathStrFixture._fields,
    PRIVATE_PATH_STR_FIXTURES,
    ids=[f.test_id for f in PRIVATE_PATH_STR_FIXTURES],
)
def test_private_path_str(
    test_id: str,
    path_suffix: str,
    expected_output: str,
) -> None:
    """Test PrivatePath string representation collapses home directory."""
    home = pathlib.Path.home()

    if path_suffix.startswith("/tmp") or path_suffix.startswith("/usr"):
        # Absolute path not under home
        input_path = pathlib.Path(path_suffix)
    elif path_suffix == "":
        # Just home
        input_path = home
    else:
        # Path under home
        input_path = home / path_suffix.lstrip("/")

    result = str(PrivatePath(input_path))
    assert result == expected_output


class PrivatePathReprFixture(t.NamedTuple):
    """Test fixture for PrivatePath repr."""

    test_id: str
    path_suffix: str
    expected_contains: str


PRIVATE_PATH_REPR_FIXTURES: list[PrivatePathReprFixture] = [
    PrivatePathReprFixture(
        test_id="repr_includes_class_name",
        path_suffix="/projects",
        expected_contains="PrivatePath",
    ),
    PrivatePathReprFixture(
        test_id="repr_shows_collapsed_path",
        path_suffix="/projects",
        expected_contains="~/projects",
    ),
]


@pytest.mark.parametrize(
    PrivatePathReprFixture._fields,
    PRIVATE_PATH_REPR_FIXTURES,
    ids=[f.test_id for f in PRIVATE_PATH_REPR_FIXTURES],
)
def test_private_path_repr(
    test_id: str,
    path_suffix: str,
    expected_contains: str,
) -> None:
    """Test PrivatePath repr includes class name and collapsed path."""
    home = pathlib.Path.home()
    input_path = home / path_suffix.lstrip("/")

    result = repr(PrivatePath(input_path))
    assert expected_contains in result


class CollapseHomeFixture(t.NamedTuple):
    """Test fixture for _collapse_home method."""

    test_id: str
    input_path: str  # Use {HOME} as placeholder
    expected_output: str


COLLAPSE_HOME_FIXTURES: list[CollapseHomeFixture] = [
    CollapseHomeFixture(
        test_id="home_exact_match",
        input_path="{HOME}",
        expected_output="~",
    ),
    CollapseHomeFixture(
        test_id="home_with_subdir",
        input_path="{HOME}/projects",
        expected_output="~/projects",
    ),
    CollapseHomeFixture(
        test_id="already_collapsed",
        input_path="~/already/collapsed",
        expected_output="~/already/collapsed",
    ),
    CollapseHomeFixture(
        test_id="non_home_path",
        input_path="/tmp/test",
        expected_output="/tmp/test",
    ),
    CollapseHomeFixture(
        test_id="similar_prefix_not_collapsed",
        input_path="{HOME}2/other",
        expected_output="{HOME}2/other",
    ),
]


@pytest.mark.parametrize(
    CollapseHomeFixture._fields,
    COLLAPSE_HOME_FIXTURES,
    ids=[f.test_id for f in COLLAPSE_HOME_FIXTURES],
)
def test_collapse_home(
    test_id: str,
    input_path: str,
    expected_output: str,
) -> None:
    """Test _collapse_home static method."""
    home = str(pathlib.Path.home())

    actual_input = input_path.replace("{HOME}", home)
    actual_expected = expected_output.replace("{HOME}", home)

    result = PrivatePath._collapse_home(actual_input)
    assert result == actual_expected


class CollapseHomeInStringFixture(t.NamedTuple):
    """Test fixture for collapse_home_in_string function."""

    test_id: str
    input_string: str  # Use {HOME} as placeholder
    expected_output: str


COLLAPSE_HOME_IN_STRING_FIXTURES: list[CollapseHomeInStringFixture] = [
    CollapseHomeInStringFixture(
        test_id="path_var_with_home",
        input_string="{HOME}/.local/bin:/usr/bin",
        expected_output="~/.local/bin:/usr/bin",
    ),
    CollapseHomeInStringFixture(
        test_id="multiple_home_paths",
        input_string="{HOME}/bin:{HOME}/.cargo/bin:/usr/bin",
        expected_output="~/bin:~/.cargo/bin:/usr/bin",
    ),
    CollapseHomeInStringFixture(
        test_id="no_home_paths",
        input_string="/usr/bin:/bin",
        expected_output="/usr/bin:/bin",
    ),
    CollapseHomeInStringFixture(
        test_id="single_path",
        input_string="{HOME}/.local/bin",
        expected_output="~/.local/bin",
    ),
]


@pytest.mark.parametrize(
    CollapseHomeInStringFixture._fields,
    COLLAPSE_HOME_IN_STRING_FIXTURES,
    ids=[f.test_id for f in COLLAPSE_HOME_IN_STRING_FIXTURES],
)
def test_collapse_home_in_string(
    test_id: str,
    input_string: str,
    expected_output: str,
) -> None:
    """Test collapse_home_in_string function."""
    home = str(pathlib.Path.home())

    actual_input = input_string.replace("{HOME}", home)

    result = collapse_home_in_string(actual_input)
    assert result == expected_output


def test_private_path_is_pathlib_compatible() -> None:
    """Test PrivatePath is compatible with pathlib.Path operations."""
    home = pathlib.Path.home()
    pp = PrivatePath(home / "test")

    # Should support path operations
    assert pp.exists() == (home / "test").exists()
    # Parent returns PrivatePath, so compare via resolve or str(with replacement)
    assert str(pp.parent) == "~"
    assert pp.name == "test"


def test_private_path_in_fstring() -> None:
    """Test PrivatePath works correctly in f-strings."""
    home = pathlib.Path.home()
    pp = PrivatePath(home / ".config" / "app")

    result = f"config: {pp}"
    assert result == "config: ~/.config/app"
    assert str(home) not in result


def test_private_path_with_non_home_path() -> None:
    """Test PrivatePath preserves paths not under home."""
    pp = PrivatePath("/etc/config")

    assert str(pp) == "/etc/config"
    assert "~" not in str(pp)
