import dataclasses

import pathlib

import typing as t

if t.TYPE_CHECKING:
    from appdirs import AppDirs as BaseAppDirs


# A sentinel object to detect if a path is supplied or not.
MISSING_DIR = pathlib.Path(str(dataclasses.MISSING.__hash__()))


@dataclasses.dataclass(frozen=True)
class AppDirs:
    """Wrap :class:`appdirs.AppDirs`'s paths in typed :class:`pathlib.Path`'s."""

    _app_dirs: dataclasses.InitVar["BaseAppDirs"]
    user_data_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    site_data_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    user_config_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    site_config_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    user_cache_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    user_state_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)
    user_log_dir: pathlib.Path = dataclasses.field(default=MISSING_DIR)

    def __post_init__(self, _app_dirs: "BaseAppDirs") -> None:
        dir_attrs = [key for key in _app_dirs.__dir__() if key.endswith("_dir")]
        dir_mapping: t.Dict[str, str] = {k: getattr(_app_dirs, k) for k in dir_attrs}
        for attr in dir_attrs:
            val = getattr(self, attr, None)
            if val is not None and isinstance(val, (str, pathlib.Path)):
                object.__setattr__(
                    self,
                    attr,
                    pathlib.Path(str(val).format(**dir_mapping)),
                )

        for attr, val in dir_mapping.items():
            # See https://docs.python.org/3.10/library/dataclasses.html#frozen-instances
            # Python 3.11 removes the recommendation to user object.__setattr__ instead
            # of super().__setattr__
            try:
                assert object.__getattribute__(self, attr) not in [
                    None,
                    MISSING_DIR,
                ]
            except (AttributeError, AssertionError):
                object.__setattr__(self, attr, pathlib.Path(val))
