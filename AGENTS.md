# AGENTS.md

unihan-etl downloads Unicode's UNIHAN CJK character database, normalizes it,
and exports it to CSV, JSON, YAML, or Python objects, via both a library API
(`Packager`, `Options`) and a `unihan-etl` CLI.

Follow the conventions already in the tree, and keep a change scoped to what
was asked for.

## What is here

| Path | What it is |
| ---- | ---------- |
| `src/unihan_etl/core.py` | ETL pipeline and `Packager`: download, extract, normalize, expand, prune, export |
| `src/unihan_etl/options.py` | `Options`, the configuration object |
| `src/unihan_etl/constants.py` | Field lists, UNIHAN-file-to-field manifest, export formats |
| `src/unihan_etl/expansion.py` | Expands multi-value fields into structured lists/dicts |
| `src/unihan_etl/cli/` | `unihan-etl` subcommands: `export`, `download`, `search`, `fields`, `files` |
| `src/unihan_etl/pytest_plugin.py` | `unihan_quick_*` / `unihan_full_*` test fixtures, shipped to consumers |
| `tests/` | Test suite |
| `docs/` | Sphinx/MyST documentation source |
| `CHANGES` | Changelog, rendered as the docs changelog page |
| `README.md` | Project overview; `README.md` is also collected by `pytest` (see WRITING.md) |

## Which policy applies

- Documentation, user-facing text, `CHANGES`, release notes, commit messages,
  docstrings, and source comments:
  [.github/WRITING.md](.github/WRITING.md)
- Environment, the gates, tests, documentation builds, releases, and pull
  requests: [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)

Each of those is the single home for its subject. Where a rule seems to be
stated twice, the file listed above is the one that governs.

## Change discipline

- Make the smallest coherent change that solves the verified problem; keep
  unrelated cleanup out of it.
- Reuse an existing file, helper, API, or test before adding a new one;
  modify in place when the change fits the file's responsibility.
- Keep a new API private until a caller outside the module needs it.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized module — not for a
  single-use helper or a one-line re-export.
- Add a test for every user-visible behaviour change, and a `CHANGES` entry
  for every change to the public API, CLI, configuration, or output.
- A passing gate is evidence only once it has been shown capable of failing.
  Pair a new test with a deliberate break that proves it bites.

## Domain facts

- Exports always prepend the index fields `char` and `ucn`, even when
  filtering to specific fields — `Packager.export` does this automatically;
  preserve it when touching export code.
- CSV export stays flat; JSON, YAML, and Python exports may nest through
  `expansion.py`. Be deliberate about which shape a change targets.
- When adding a UNIHAN field, update both the manifest and the allowed-field
  list in `constants.py` — they are read together.
- `Packager.from_cli` and the three `command_*` CLI functions
  (`cli/search.py`, `cli/export.py`, `cli/download.py`) all catch
  `Exception` broadly at the CLI boundary; only `from_cli` needs a
  `BLE001` ignore, because the other three log the traceback first (see
  WRITING.md).

## References

- Docs: <https://unihan-etl.git-pull.com>
- CLI reference: <https://unihan-etl.git-pull.com/en/latest/cli.html>
- Unicode UNIHAN spec: <https://www.unicode.org/reports/tr38/>
- cihai project: <https://cihai.git-pull.com>
- gp-libs (shared dev/test/doctest tooling used here): <https://gp-libs.git-pull.com>
