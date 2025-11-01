"""Tests for unihan_etl._internal.app_dirs."""

from __future__ import annotations

import dataclasses
import pathlib
import typing as t
from collections.abc import Mapping

import pytest
from appdirs import AppDirs as BaseAppDirs

from unihan_etl._internal.app_dirs import AppDirs

AppDirsInitParams = dict[str, t.Any]
ExpectedAppDirsParam = Mapping[str, str | pathlib.Path]


class AppDirFixture(t.NamedTuple):
    """Pytest fixture for AppDir."""

    # pytest
    test_id: str

    # Environment vars
    env: dict[str, str]

    # Configuration
    app_dirs_init_params: AppDirsInitParams

    # Expected
    expected_app_dirs: ExpectedAppDirsParam


APP_DIR_FIXURES = [
    AppDirFixture(
        test_id="basic",
        env={},
        app_dirs_init_params={},
        expected_app_dirs={},
    ),
    AppDirFixture(
        test_id="env-xdg-config-home",
        env={"XDG_CONFIG_HOME": "{tmp_path}/.config"},
        app_dirs_init_params={},
        expected_app_dirs={
            "user_config_dir": pathlib.Path("{tmp_path}/.config"),
        },
    ),
    AppDirFixture(
        test_id="env-xdg-cache-home",
        env={"XDG_CACHE_HOME": "{tmp_path}/.cache"},
        app_dirs_init_params={},
        expected_app_dirs={
            "user_cache_dir": pathlib.Path("{tmp_path}/.cache"),
        },
    ),
    AppDirFixture(
        test_id="direct-override-user-cache-dir",
        env={},
        app_dirs_init_params={"user_cache_dir": "{tmp_path}/.cache"},
        expected_app_dirs={
            "user_cache_dir": pathlib.Path("{tmp_path}/.cache"),
        },
    ),
]


@pytest.mark.parametrize(
    list(AppDirFixture._fields),
    APP_DIR_FIXURES,
    ids=[test.test_id for test in APP_DIR_FIXURES],
)
def test_basic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    test_id: str,
    env: dict[str, str],
    app_dirs_init_params: AppDirsInitParams,
    expected_app_dirs: ExpectedAppDirsParam,
) -> None:
    """Test basic usage of AppDirs."""
    # Setup
    for k, v in env.items():
        monkeypatch.setenv(k, v.format(tmp_path=str(tmp_path)))

    for k, v in app_dirs_init_params.items():
        app_dirs_init_params[k] = v.format(tmp_path=str(tmp_path))

    # Initialize
    app_dirs_ = BaseAppDirs()
    app_dirs = AppDirs(_app_dirs=app_dirs_, **app_dirs_init_params)

    # Assert
    for field in dataclasses.fields(app_dirs):
        assert isinstance(getattr(app_dirs, field.name), pathlib.Path)

    for exp_k, exp_v in expected_app_dirs.items():
        if isinstance(exp_v, pathlib.Path):
            exp_v = pathlib.Path(str(exp_v).format(tmp_path=str(tmp_path)))
        if isinstance(exp_v, str):
            exp_v = exp_v.format(tmp_path=str(tmp_path))
        assert getattr(app_dirs, exp_k) == exp_v
