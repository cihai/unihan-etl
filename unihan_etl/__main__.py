#!/usr/bin/env python
"""For accessing cihai as a package."""

import os
import sys
import typing as t

if t.TYPE_CHECKING:
    from typing_extensions import TypeAlias

    # see https://github.com/python/typeshed/issues/8513#issue-1333671093 for the
    # rationale behind this alias
    _ExitCode: TypeAlias = t.Optional[t.Union[str, int]]


def run() -> "_ExitCode":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base)
    from .process import Packager

    p = Packager.from_cli(sys.argv[1:])
    p.download()
    p.export()

    return 0


if __name__ == "__main__":
    sys.exit(run())
