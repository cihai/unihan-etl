import dataclasses
import os
import pathlib
import typing as t

if t.TYPE_CHECKING:
    from appdirs import AppDirs as BaseAppDirs


MISSING_DIR = pathlib.Path(str(dataclasses.MISSING.__hash__()))
"""A sentinel object to detect if a path is supplied or not.

:meta hide-value:
"""


@dataclasses.dataclass(frozen=True)
class AppDirs:
    """Wrap :class:`appdirs.AppDirs`'s paths in typed :class:`pathlib.Path`'s.

    Retrieve directories as dataclass in :class:`pathlib.Path` format:

    >>> from appdirs import AppDirs as BaseAppDirs
    >>> app_dirs = AppDirs(_app_dirs=BaseAppDirs())
    >>> app_dirs.user_log_dir
    PosixPath('.../log')

    Override directories:

    >>> app_dirs = AppDirs(_app_dirs=BaseAppDirs(), user_log_dir='/var/log/myapp')
    >>> app_dirs.user_log_dir
    PosixPath('/var/log/myapp')

    Replace environment variables via :class:`os.expandfars`:

    >>> import os
    >>> os.environ['my_cache_var'] = '/var/cache/'
    >>> app_dirs = AppDirs(
    ...     _app_dirs=BaseAppDirs(), user_cache_dir='${my_cache_var}/myapp'
    ... )
    >>> app_dirs.user_cache_dir
    PosixPath('/var/cache/myapp')

    Support for XDG environmental variables:

    >>> import os
    >>> os.environ['XDG_CACHE_HOME'] = '/var/cache/'
    >>> app_dirs = AppDirs(_app_dirs=BaseAppDirs())
    >>> app_dirs.user_cache_dir
    PosixPath('/var/cache')
    """

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
                    pathlib.Path(
                        os.path.expanduser(  # noqa: PTH111
                            os.path.expandvars(str(val)),
                        ).format(**dir_mapping)
                    ),
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
            except (AttributeError, AssertionError):  # ruff: noqa: PERF203
                object.__setattr__(
                    self,
                    attr,
                    pathlib.Path(
                        os.path.expanduser(  # noqa: PTH111
                            os.path.expandvars(str(val)),
                        ).format(**dir_mapping)
                    ),
                )
