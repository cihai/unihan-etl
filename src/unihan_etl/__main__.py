#!/usr/bin/env python
"""Run unihan-etl as a CLI tool."""

from __future__ import annotations

import sys
import typing as t

if t.TYPE_CHECKING:
    from typing import TypeAlias

    # see https://github.com/python/typeshed/issues/8513#issue-1333671093 for the
    # rationale behind this alias
    _ExitCode: TypeAlias = str | int | None


def run() -> _ExitCode:
    """Execute unihan-etl via CLI entrypoint."""
    from unihan_etl.cli import cli

    return cli()


if __name__ == "__main__":
    sys.exit(run())
