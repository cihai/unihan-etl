import dataclasses

import pathlib

import typing as t

if t.TYPE_CHECKING:
    from appdirs import AppDirs as BaseAppDirs


@dataclasses.dataclass(frozen=True)
class AppDirs:
    """Wrap :class:{appdirs.AppDirs}'s paths in typed :class:`pathlib.Path`'s."""

    user_data_dir: pathlib.Path = dataclasses.field(init=False)
    site_data_dir: pathlib.Path = dataclasses.field(init=False)
    user_config_dir: pathlib.Path = dataclasses.field(init=False)
    site_config_dir: pathlib.Path = dataclasses.field(init=False)
    user_cache_dir: pathlib.Path = dataclasses.field(init=False)
    user_state_dir: pathlib.Path = dataclasses.field(init=False)
    user_log_dir: pathlib.Path = dataclasses.field(init=False)
    _app_dirs: dataclasses.InitVar["BaseAppDirs"]

    def __post_init__(self, _app_dirs: "BaseAppDirs") -> None:
        # See https://docs.python.org/3.10/library/dataclasses.html#frozen-instances
        # Python 3.11 removes the recommendation to user object.__setattr__ instead
        # of super().__setattr__
        object.__setattr__(self, "user_data_dir", pathlib.Path(_app_dirs.user_data_dir))
        object.__setattr__(self, "site_data_dir", pathlib.Path(_app_dirs.site_data_dir))
        object.__setattr__(
            self, "user_config_dir", pathlib.Path(_app_dirs.user_config_dir)
        )
        object.__setattr__(
            self, "site_config_dir", pathlib.Path(_app_dirs.site_config_dir)
        )
        object.__setattr__(
            self, "user_cache_dir", pathlib.Path(_app_dirs.user_cache_dir)
        )
        object.__setattr__(
            self, "user_state_dir", pathlib.Path(_app_dirs.user_state_dir)
        )
        object.__setattr__(self, "user_log_dir", pathlib.Path(_app_dirs.user_log_dir))
