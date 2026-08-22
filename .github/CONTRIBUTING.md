# Contributing

Thanks for looking. Bug reports with a reproduction, and documentation fixes
where UNIHAN's own quirks misled you, are the most useful contributions right
now.

How this project writes prose — README, `CHANGES`, release notes, commit
messages, CLI help text, error messages, docstrings, and source comments — is
set out separately in [WRITING.md](WRITING.md). Read that before changing
any of it. The constraints every change is held to, and the map of what is
where, are in [AGENTS.md](../AGENTS.md).

## Getting set up

```console
$ uv sync --all-extras --dev
```

## The gates

Format:

```console
$ uv run ruff format .
```

Lint:

```console
$ uv run ruff check . --fix --show-fixes
```

Type-check:

```console
$ uv run mypy .
```

`mypy` runs in strict mode. `[tool.mypy]` in `pyproject.toml` sets `files =
["src/", "tests/"]`, but the `.` argument to `mypy .` above overrides that
setting, so the gate actually type-checks everything under the repo root,
including `docs/conf.py`.

Test:

```console
$ uv run py.test
```

Documentation is a gate, not a courtesy. Examples in docstrings, pages under
`docs/`, and `README.md` are executed by `pytest` — the doctest flags live in
`pyproject.toml`, so there is no separate doctest step and a green `py.test`
is the proof. Which blocks qualify, and the one mistake that silently removes
a test, are in
[WRITING.md](WRITING.md#documented-examples-that-run).

Before claiming a test or a gate works, show it failing. A gate that has
never been red is an assumption.

CI (`.github/workflows/tests.yml`) runs `ruff check`, `ruff format --check`,
`mypy .`, and `py.test --cov=./ --cov-report=xml` on every push and pull
request across Python 3.10, 3.11, 3.12, and 3.14 (3.13 is not in the
matrix); it is the order of record.

## Tests

Prefer the pytest plugin's fixtures (`unihan_quick_*`, `unihan_full_*`) over
an ad-hoc download. `unihan_quick_*` builds a small synthetic UNIHAN subset
for fast unit tests; `unihan_full_*` mirrors the complete dataset and is
slower and heavier. Both cache under the project-local `.unihan_cache/`
directory (`unihan_project_cache_path` in `pytest_plugin.py`) so repeat runs
skip the network — avoid touching that path directly from a test.

`unihan_full_*` and `unihan_quick_*` are session-scoped and shared across
workers: `_cache_lock` in `pytest_plugin.py` is a no-op outside `pytest-xdist`
and a `filelock.FileLock` under it (`test_xdist_safety.py` covers both
paths), so `-n auto` (`just test-dist`) cannot corrupt a cache two workers
race to build.

The root `conftest.py`'s `set_home` fixture (autouse) points `HOME` at a
fixture-managed path for every test, and seeds `.unihan_zshrc` under zsh —
tests never read or write a real user profile.

Favor `tmp_path` over manual tempfile handling, and `monkeypatch` and
fixtures before reaching for mocks. Add a docstring example to show CLI or
library usage only when it is short and stable; move a longer flow into a
test file under `tests/`.

Re-run the tests on every change with
[pytest-watcher](https://github.com/olzhasar/pytest-watcher):

```console
$ uv run ptw .
```

Scan for dead code with [vulture](https://github.com/jendrikseipp/vulture):

```console
$ just vulture
```

When stuck after a few failed attempts on a test or a gate: stop, strip to a
minimal reproduction, capture the exact error, and write down what has been
tried before continuing — repeated attempts with escalating complexity are a
sign to reset, not push through.

## Logging

These rules guide future logging changes; existing code may not yet conform.

**Logger setup.** Use `logging.getLogger(__name__)` in every module. Add a
`NullHandler` in library `__init__.py` files. Never configure handlers,
levels, or formatters in library code — that is the application's job.

**Structured context via `extra`.** Pass structured data on every log call
useful for filtering, searching, or test assertions.

Core keys (stable, scalar, safe at any log level):

| Key                    | Type       | Context                     |
| ---------------------- | ---------- | ---------------------------- |
| `unihan_field`         | `str`      | UNIHAN field name            |
| `unihan_source_file`   | `str`      | source data file path        |
| `unihan_record_count`  | `int`      | records processed            |
| `unihan_format`        | `str`      | export format (csv/json/yaml)|

Heavy/optional keys (DEBUG only, potentially large):

| Key               | Type        | Context                                            |
| ------------------ | ----------- | --------------------------------------------------- |
| `unihan_stdout`   | `list[str]` | subprocess stdout lines (truncate or cap)           |
| `unihan_stderr`   | `list[str]` | subprocess stderr lines (same caveats)              |

Treat established keys as compatibility-sensitive — downstream users may
build dashboards and alerts on them. Change deliberately. Key names are
`snake_case` with a `unihan_` prefix; prefer stable scalars over ad-hoc
objects.

**Lazy formatting.** `logger.debug("msg %s", val)`, not f-strings: the
interpolation is skipped entirely when the level is filtered, and a
log-aggregator groups `"Running %s"` as one signature instead of ten
thousand unique f-string lines. Guard an expensive `val` with
`if logger.isEnabledFor(logging.DEBUG)`.

**`stacklevel` for wrappers.** Increment it for each wrapper layer so
`%(filename)s:%(lineno)d` and OpenTelemetry's `code.filepath` point to the
real caller. Verify whenever call depth changes.

**`LoggerAdapter` for persistent context.** For objects with stable
identity, use `LoggerAdapter` (override `process()` to merge `extra`) rather
than repeating the same `extra` on every call; `merge_extra=True` simplifies
this on Python 3.13+.

**Log levels.**

| Level     | Use for                                   | Examples                                      |
| --------- | ------------------------------------------ | ---------------------------------------------- |
| `DEBUG`   | Internal mechanics, data I/O               | Field parsing, record transformation steps     |
| `INFO`    | Data lifecycle, user-visible operations    | Download completed, export finished            |
| `WARNING` | Recoverable issues, deprecation, bad config| Missing optional field, deprecated data format |
| `ERROR`   | Failures that stop an operation            | Download failed, parse error, write failed     |

Config discovery noise belongs in `DEBUG`; only a surprising or
user-actionable config issue goes to `WARNING`.

**Message style.** Lowercase, past tense for events: `"download completed"`,
`"parse error"`. No trailing punctuation. Keep messages short; put details in
`extra`, not the message string.

**Exception logging.** Use `logger.exception()` only inside an `except` block
when not re-raising. Use `logger.error(..., exc_info=True)` for a traceback
needed outside an `except` block. Avoid `logger.exception()` followed by
`raise` — that duplicates the traceback; either add `extra` context that
would otherwise be lost, or let the exception propagate.

**Testing logs.** Assert on `caplog.records` attributes, not string matching
on `caplog.text`. Scope capture with
`caplog.at_level(logging.DEBUG, logger="unihan_etl.process")`; filter records
rather than index by position; assert on schema
(`record.unihan_record_count == 100`, not `"100 records" in caplog.text`).
`caplog.record_tuples` cannot access extra fields — use `caplog.records`.

**Avoid:** f-strings/`.format()` in log calls; unguarded logging in hot
loops; catch-log-reraise without adding context; `print()` for diagnostics;
logging secret env var values (log key names only); non-scalar ad-hoc
objects in `extra`; custom `extra` fields referenced in format strings
without safe defaults (a missing key raises `KeyError`).

## Coding standards

- Begin every module with `from __future__ import annotations` — `ruff`'s
  isort `required-imports` enforces this.
- Prefer namespace imports for the standard library (`import typing as t`,
  `import pathlib`); third-party packages may use `from X import Y`.
- NumPy-style docstrings in reStructuredText for public APIs, enforced by
  `ruff`'s `pydocstyle` convention.
- Keep a doctest short and narrative; move a complex flow into
  `tests/examples/**` instead of a docstring.

## Documentation

Build the Sphinx docs:

```console
$ just build-docs
```

Serve with autobuild:

```console
$ just start-docs
```

Rebuild the CSS/JS design assets:

```console
$ just design-docs
```

## Releasing

Never create tags. Never push tags. The owner handles tagging and tag
pushes, because a tag triggers the publish workflow. See
[Release commits](WRITING.md#release-commits).

unihan-etl follows [semantic versioning](https://semver.org/); until 1.0, a
minor release may include a breaking API change. The owner's release
checklist: update `CHANGES` with the new entries under the next version
heading, bump the version in `pyproject.toml`, commit as `Tag vX.Y.Z`, tag
`vX.Y.Z`, and `git push --follow-tags` — the tagged push triggers
`.github/workflows/tests.yml`'s `release` job, which builds and publishes to
PyPI.

## Pull requests

One subject per pull request. Unrelated cleanup found along the way belongs
in its own commit, and usually in its own pull request.

Discuss a substantial change via an issue before making it.

Commit format is in [WRITING.md](WRITING.md#commits).

## Decorum

- Participants will be tolerant of opposing views.
- Participants must ensure that their language and actions are free of
  personal attacks and disparaging personal remarks.
- When interpreting the words and actions of others, participants should
  always assume good intentions.
- Behaviour which can be reasonably considered harassment will not be
  tolerated.

Based on [Ruby's Community Conduct Guideline](https://www.ruby-lang.org/en/conduct/).

## Security

Please do not open a public issue for a vulnerability. Use GitHub's private
vulnerability reporting for this repository (the "Report a vulnerability"
link under the Security tab) instead.
