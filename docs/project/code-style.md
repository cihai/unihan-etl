(code-style)=

# Code Style

## Formatting and linting

unihan-etl uses [ruff](https://docs.astral.sh/ruff/) for both formatting and linting.

```console
$ uv run ruff format .
```

```console
$ uv run ruff check . --fix --show-fixes
```

## Type checking

[mypy](https://mypy.readthedocs.io/) runs in strict mode.

```console
$ uv run mypy src tests
```

## Docstrings

Follow [NumPy-style](https://numpydoc.readthedocs.io/en/latest/format.html) docstrings
in reStructuredText format.

## Imports

- Begin every module with `from __future__ import annotations`.
- Prefer namespace imports for stdlib: `import typing as t`, `import pathlib`.
- Third-party packages may use `from X import Y`.
