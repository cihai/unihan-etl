# AGENTS.md

Guidance for AI agents (Claude Code, Cursor, et al.) working in this repository.

## CRITICAL REQUIREMENTS

### Test Success
- ALL tests MUST pass before you describe changes as complete.
- Do not claim the code "works" while any test, lint, or type check fails.
- Fix regressions introduced by your changes; do not mark work finished with broken CI.
- Successful work means: formatting, linting, type checking, and test suites are all green.

## Project Overview

unihan-etl is a Python ETL tool that downloads the Unicode UNIHAN database, normalizes it, and exports it in multiple formats (CSV, JSON, YAML, or Python objects). It provides both a library API and a CLI for fetching, expanding, and pruning UNIHAN fields. The library is typed and ships pytest fixtures for quickly bootstrapping test datasets.

Key capabilities:
- Download, cache, and validate official UNIHAN releases.
- Convert UNIHAN text files into tabular or structured exports.
- Options to expand multi-value fields and prune empty values.
- Typed Python API plus CLI entry point for batch exports.
- Pytest plugin supplying ready-to-use quick/full datasets.

## Development Environment

This project uses:
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- [ruff](https://github.com/astral-sh/ruff) for linting/formatting
- [mypy](https://github.com/python/mypy) for type checking
- [pytest](https://docs.pytest.org/) for testing
- [gp-libs](https://gp-libs.git-pull.com) for shared dev tooling (docs/test helpers)

## Common Commands

### Setting Up Environment

```bash
# Install dependencies (editable)
uv pip install --editable .
uv pip sync

# Install with development extras
uv pip install --editable . -G dev
```

### Running Tests

```bash
# Run all tests
just test          # -> uv run py.test
# or directly
uv run py.test

# Watch tests
just start         # runs tests once then starts ptw
uv run ptw .

# Dead code scan
just vulture
```

### Linting and Type Checking

```bash
# Lint
just ruff
uv run ruff check .

# Format
just ruff-format
uv run ruff format .

# Lint with fixes
uv run ruff check . --fix --show-fixes

# Type check
just mypy
uv run mypy src tests
```

### Documentation

```bash
just build-docs     # build Sphinx docs
just start-docs     # autobuild + serve
just design-docs    # rebuild CSS/JS assets
```

## Code Architecture

1. **core.py** (`src/unihan_etl/core.py`)  
   - Houses the ETL pipeline and `Packager` class: download, extract, normalize, expand, prune, and export UNIHAN data.
   - CLI entry helpers (`from_cli`) and export writers (CSV/JSON/YAML/Python).
2. **options.py** (`src/unihan_etl/options.py`)  
   - Dataclass-like configuration object with defaults for paths, formats, caching, logging, and selected fields/files.
3. **constants.py** (`src/unihan_etl/constants.py`)  
   - Field lists, manifest mapping of UNIHAN files to fields, default paths, and allowed export formats.
4. **expansion.py** (`src/unihan_etl/expansion.py`)  
   - Expands multi-value UNIHAN fields into structured lists/dicts; handles delimiters and nested data.
5. **util.py** (`src/unihan_etl/util.py`)  
   - Helpers for progress display, field resolution, Unicode codepoint handling (`ucn_to_unicode`), and manifest utilities.
6. **types.py** (`src/unihan_etl/types.py`)  
   - Shared TypedDicts/TypeAliases for exported structures and options.
7. **pytest_plugin.py** (`src/unihan_etl/pytest_plugin.py`)  
   - Pytest fixtures for “quick” (small) and “full” (complete) UNIHAN datasets; manages cache locations and packagers.
8. **__main__.py / test.py**  
   - CLI entry point (`python -m unihan_etl`) and legacy test harness.

## Testing Strategy

- Prefer the provided pytest fixtures (`unihan_quick_*`, `unihan_full_*`) instead of ad-hoc downloads; they bootstrap caches and zip fixtures for deterministic tests.
- Quick fixtures create a small synthetic UNIHAN subset suitable for fast unit tests; full fixtures mirror the complete dataset and may be slower/heavier.
- Use `uv run ptw .` or `just start` for watch mode during development.
- When adding new fixtures, keep them under the existing cache paths defined in `pytest_plugin.py`.
- Avoid network access in unit tests; rely on cached zips or local fixtures.

### Testing Guidelines
- Favor `tmp_path` over manual tempfile handling.
- Use `monkeypatch` and fixtures before reaching for mocks.
- Add docstring examples to showcase CLI/library usage only when short and stable; move longer examples to dedicated test files under `tests/`.

## Coding Standards

- Always begin Python modules with `from __future__ import annotations`.
- Prefer namespace imports for stdlib (`import typing as t`, `import pathlib`, etc.); third-party packages may use `from X import Y`.
- Use NumPy-style docstrings in reStructuredText format for public APIs.
- Format before review: `uv run ruff format .`; then lint (`uv run ruff check . --fix --show-fixes`); then type-check (`uv run mypy`); re-run tests.
- Doctests: keep short, narrative examples in docstrings; move complex flows into `tests/examples/**`.
- Pytest: favor existing fixtures and `tmp_path`/`monkeypatch` instead of heavy mocks.
- Avoid debug loops: if stuck after a few failed attempts, pause, strip to a minimal repro, capture exact errors, and write a concise summary before retrying.

## Logging Standards

These rules guide future logging changes; existing code may not yet conform.

### Logger setup

- Use `logging.getLogger(__name__)` in every module
- Add `NullHandler` in library `__init__.py` files
- Never configure handlers, levels, or formatters in library code — that's the application's job

### Structured context via `extra`

Pass structured data on every log call where useful for filtering, searching, or test assertions.

**Core keys** (stable, scalar, safe at any log level):

| Key | Type | Context |
|-----|------|---------|
| `unihan_field` | `str` | UNIHAN field name |
| `unihan_source_file` | `str` | source data file path |
| `unihan_record_count` | `int` | records processed |
| `unihan_format` | `str` | export format (csv, json, yaml) |

**Heavy/optional keys** (DEBUG only, potentially large):

| Key | Type | Context |
|-----|------|---------|
| `unihan_stdout` | `list[str]` | subprocess stdout lines (truncate or cap; `%(unihan_stdout)s` produces repr) |
| `unihan_stderr` | `list[str]` | subprocess stderr lines (same caveats) |

Treat established keys as compatibility-sensitive — downstream users may build dashboards and alerts on them. Change deliberately.

### Key naming rules

- `snake_case`, not dotted; `unihan_` prefix
- Prefer stable scalars; avoid ad-hoc objects
- Heavy keys (`unihan_stdout`, `unihan_stderr`) are DEBUG-only; consider companion `unihan_stdout_len` fields or hard truncation (e.g. `stdout[:100]`)

### Lazy formatting

`logger.debug("msg %s", val)` not f-strings. Two rationales:
- Deferred string interpolation: skipped entirely when level is filtered
- Aggregator message template grouping: `"Running %s"` is one signature grouped ×10,000; f-strings make each line unique

When computing `val` itself is expensive, guard with `if logger.isEnabledFor(logging.DEBUG)`.

### stacklevel for wrappers

Increment for each wrapper layer so `%(filename)s:%(lineno)d` and OTel `code.filepath` point to the real caller. Verify whenever call depth changes.

### LoggerAdapter for persistent context

For objects with stable identity (Dataset, Reader, Exporter), use `LoggerAdapter` to avoid repeating the same `extra` on every call. Lead with the portable pattern (override `process()` to merge); `merge_extra=True` simplifies this on Python 3.13+.

### Log levels

| Level | Use for | Examples |
|-------|---------|----------|
| `DEBUG` | Internal mechanics, data I/O | Field parsing, record transformation steps |
| `INFO` | Data lifecycle, user-visible operations | Download completed, export finished, database bootstrapped |
| `WARNING` | Recoverable issues, deprecation, user-actionable config | Missing optional field, deprecated data format |
| `ERROR` | Failures that stop an operation | Download failed, parse error, database write failed |

Config discovery noise belongs in `DEBUG`; only surprising/user-actionable config issues → `WARNING`.

### Message style

- Lowercase, past tense for events: `"download completed"`, `"parse error"`
- No trailing punctuation
- Keep messages short; put details in `extra`, not the message string

### Exception logging

- Use `logger.exception()` only inside `except` blocks when you are **not** re-raising
- Use `logger.error(..., exc_info=True)` when you need the traceback outside an `except` block
- Avoid `logger.exception()` followed by `raise` — this duplicates the traceback. Either add context via `extra` that would otherwise be lost, or let the exception propagate

### Testing logs

Assert on `caplog.records` attributes, not string matching on `caplog.text`:
- Scope capture: `caplog.at_level(logging.DEBUG, logger="unihan_etl.process")`
- Filter records rather than index by position: `[r for r in caplog.records if hasattr(r, "unihan_field")]`
- Assert on schema: `record.unihan_record_count == 100` not `"100 records" in caplog.text`
- `caplog.record_tuples` cannot access extra fields — always use `caplog.records`

### Avoid

- f-strings/`.format()` in log calls
- Unguarded logging in hot loops (guard with `isEnabledFor()`)
- Catch-log-reraise without adding new context
- `print()` for diagnostics
- Logging secret env var values (log key names only)
- Non-scalar ad-hoc objects in `extra`
- Requiring custom `extra` fields in format strings without safe defaults (missing keys raise `KeyError`)

## Git Commit Standards

Commit subjects: `Scope(type[detail]): concise description`

Body template:
```
why: Reason or impact.

what:
- Key technical changes
- Single topic only
```

Guidelines:
- Subject ≤50 chars; body lines ≤72 chars; imperative mood.
- One topic per commit; separate subject and body with a blank line.
- Examples: `Packager(fix[export]): Handle empty fields`, `py(deps[dev]): Update pytest to v8.1`.

Common commit types:
- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (CLAUDE.md)
- **ai(claude[command])**: Claude Code command changes

#### Release commits

Never create tags. Never push tags. The user handles tagging and tag
pushes (tags trigger the CI publish workflow).

Release commit subjects are plain and short: `Tag v<version>`. Put
the detailed why/what in the commit body. Don't use the
`Scope(type[detail]):` format for releases — don't bury the lede.

## Documentation Standards

### CHANGES File

When editing the CHANGES file, **never delete** these markers in the unreleased section:

```markdown
<!-- Maintainers, insert changes / features for the next release here -->

_Add your latest changes from PRs here_
```

Insert new entries **after** these markers, not in place of them.

### Code Blocks in Documentation

When writing documentation (README, CHANGES, docs/), follow these rules for code blocks:

**One command per code block.** This makes commands individually copyable.

**Put explanations outside the code block**, not as comments inside.

Good:

Run the tests:

```console
$ uv run pytest
```

Run with coverage:

```console
$ uv run pytest --cov
```

Bad:

```console
# Run the tests
$ uv run pytest

# Run with coverage
$ uv run pytest --cov
```

### Changelog Conventions

These rules apply when authoring entries in `CHANGES`, which is rendered as the Sphinx changelog page. Modeled on Django's release-notes shape — deliverables get titles and prose, not bullets. Older entries used a flat `### Section` + bullet shape; new entries follow the Django shape below.

**Release entry boilerplate.** Every release header is `## unihan-etl X.Y.Z (YYYY-MM-DD)`. The file opens with a `## unihan-etl X.Y.Z (unreleased)` placeholder block fenced by `<!-- KEEP THIS PLACEHOLDER ... -->` and `<!-- END PLACEHOLDER ... -->` HTML comments — new release entries land immediately below the END marker, never above it.

**Open with a multi-sentence lead paragraph.** Plain prose, no italic. Open with the version as sentence subject (*"unihan-etl X.Y.Z ships …"*) so the lead is self-contained when excerpted. Two to four sentences telling the reader what shipped and who cares — user-visible takeaways, not internal mechanism. Cross-reference detail docs with `{ref}` to keep the lead compact.

**Lead paragraphs are release-time material — off-limits to branches and PRs.** The unreleased entry carries no lead paragraph and no version summary: sections only (`### Breaking changes`, `### What's new` deliverables, `### Fixes`, …). Speaking for the release — what the version "is", "ships", or "focuses on" — is presumptuous before its scope is final; only the person cutting the release writes that, and only when the user explicitly asks to release. Never write or edit a lead from a feature branch, and never ask or imply that a release should happen.

**Each deliverable is a section, not a bullet.** Inside `### What's new`, every distinct deliverable gets a `#### Deliverable title (#NN)` heading naming it in user vocabulary, followed by 1-3 prose paragraphs explaining what shipped. Don't wrap a paragraph in `- ` — bullets are for enumerable lists, not paragraph containers. Cross-link detail docs (`See {ref}\`foo\` for details.`) so prose stays focused.

**The deliverable test.** Before writing an entry, ask: "What's the deliverable, in user vocabulary?" If you can't answer in one sentence, the entry isn't ready. Mechanism (helper internals, byte counters, schema-validation locations) belongs in PR descriptions and code comments, not the changelog.

**Fixed subheadings**, in this order when present: `### Breaking changes`, `### Dependencies`, `### What's new`, `### Fixes`, `### Documentation`, `### Development`. Dev tooling (helper scripts, internal automation) lives under `### Development`. For breaking changes, show the migration path with concrete inline code (e.g. a `# Before` / `# After` fenced code block). Dependency floor bumps use the form ``Minimum `pkg>=X.Y.Z` (was `>=X.Y.W`)``.

**PR refs `(#NN)`** sit in each deliverable's `####` heading.

**When bullets are appropriate.** Catch-all sections (`### Fixes`, occasionally `### Documentation`) with 3+ genuinely small items use bullets — one line each, never paragraphs. If a bullet swells past two lines, promote it to a `#### Title (#NN)` heading with prose body.

**Anti-patterns.**

- Fragile metrics: token ceilings, third-party version pins, percent benchmarks, exact byte counts. Describe the *capability*, not the math.
- Internal jargon: private symbols (leading-underscore identifiers), algorithm names exposed for the first time, backend scaffolding.
- Walls of text dressed up as bullets.
- Buried breaking changes — they get their own subheading at the top of the entry.

**Always link autodoc'd APIs.** Any class, method, function, exception, or attribute that has its own rendered page must be cited via the appropriate role (`{class}`, `{meth}`, `{func}`, `{exc}`, `{attr}`) — never with plain backticks. Doc pages without explicit ref labels use `{doc}`. Plain backticks are correct for code syntax, env vars, parameter names, and file paths that aren't doc pages — anything without an autodoc destination.

**MyST roles.** Class references use `{class}`, methods use `{meth}`, functions use `{func}`, exceptions use `{exc}`, attributes use `{attr}`, internal anchors use `{ref}`, doc-path links use `{doc}`.

**Summarization style.** When a user asks "what changed in the latest version?" or similar, lead with the entry's lead paragraph (paraphrased if needed), followed by each `####` deliverable heading under `### What's new` with a one-sentence summary. Cite `(#NN)` only if the user asks for source links. Don't invent versions, dates, or numbers not present in `CHANGES`. Don't quote line numbers or file offsets — those shift as the file evolves.

## Debugging Tips

- Detect loops: repeated failing attempts, escalating complexity, unclear root cause.
- Reset to MVP: remove experimental code, keep smallest repro.
- Document clearly (inputs, outputs, errors, attempted fixes, hypothesis) before the next iteration.

## Notes and Docs

- When editing markdown under `notes/**`, keep it concise, structured with headings/lists, and mark code with fenced blocks.
- Link syntax for external PRs should be regular Markdown; keep redundancy low.

## Domain-Specific Notes

- UNIHAN manifests live in `constants.py`; when adding fields, update both manifest and allowed field lists.
- Exports must include index fields (`char`, `ucn`) even when filtering; `Packager.export` prepends them automatically—preserve this behavior.
- CSV exports stay flat; structured exports (JSON/YAML/Python) may expand to nested structures; be mindful when altering expansion rules in `expansion.py`.
- Large downloads are cached under `.unihan_cache` (by fixtures). Respect cache paths to avoid redundant downloads in CI.

## References

- Docs: https://unihan-etl.git-pull.com
- CLI reference: https://unihan-etl.git-pull.com/en/latest/cli.html
- Unicode UNIHAN spec: https://www.unicode.org/reports/tr38/
- cihai project: https://cihai.git-pull.com
- gp-libs (shared tooling used here): https://gp-libs.git-pull.com

## AI Slop Prevention

Treat AI slop as **review-hostile noise**, not as proof that text or
code is wrong. The goal is to maximize information density by removing
artifacts that make the repository harder to trust or navigate.

### The Anti-Slop Rubric

Before committing, audit all AI-assisted changes for these noise
patterns:

- **AI Signatures:** Remove "Generated by", footers, conversational
  filler ("Certainly!", "Here is..."), unexplained emojis (🤖, ✨), and
  AI-tool metadata.
- **Brittle References:** Avoid hard-coded line numbers, fragile
  file/test counts, dated "as of" claims, bare SHAs, and local
  absolute paths unless they are strict evidentiary artifacts (e.g.,
  benchmark logs).
- **Diff Narration:** Do not restate what moved, was renamed, or was
  removed in artifacts the downstream reader holds: code, docstrings,
  README, CHANGES, PR descriptions, or release notes. The diff and
  commit message already carry this history.
- **Branch-Internal Narrative:** Do not mention intermediate branch
  states, abandoned approaches, or "no longer" behavior unless users
  of a published release actually experienced the old state (**The
  Published-Release Test**).
- **Low-Value Scaffolding:** Remove ownerless TODOs (`TODO: revisit`),
  unused future-proofing, debug artifacts, and defensive wrappers that
  do not protect a currently reachable failure mode.
- **Prose Inflation:** Replace generic AI "tells" like *comprehensive,
  robust, seamless, production-ready, leverage, delve, tapestry,* and
  *best practices* with concrete descriptions of behavior,
  constraints, or trade-offs.
- **Coded Labels:** Write rules, options, and findings as plain
  imperatives. Don't tag them with codes like `[R1]`, `A1`, or
  `Option B` in artifacts a human reads — the reader shouldn't have to
  decode an index. Internal agent bookkeeping may use ids; shipped text
  may not.

### Durable Source Links

Link to a pinned revision, never to trunk. A pinned permalink is not a
brittle reference; an unlinked SHA dropped into prose is. `blob/master/…`
links rot silently — the file moves, lines shift, and the anchor lands
on unrelated code while still resolving.

- Prefer a release tag (`blob/v1.4.0/…`). Most durable, and it tells
  the reader which released version the claim held for.
- Otherwise use a 7-char commit ref (`blob/9a29b1a/…`) reachable from
  trunk. Use when there is no tag or the claim is about unreleased
  code. Never a PR-head SHA — it can be rebased or garbage-collected.
- Reserve `blob/master/…` for living documents meant to always show the
  latest state, such as a contributing guide.
- Line anchors (`#L120-L145`) are only safe on a pinned ref.

### Preservation & Context

**When unsure, leave the text in place and ask.** Subjective cleanup
must never be a reason to remove load-bearing rationale.

- **Preserve the "Why":** You MUST NOT delete comments that document
  invariants, protocol constraints, platform quirks, security
  boundaries, and upstream workarounds.
- **Evidence is Immune:** Preserve exact counts, dates, and SHAs when
  they serve as evidence in benchmark results, release notes, stack
  traces, or lockfiles.
- **Behavior Over Inventory:** A useful description explains what
  changed for the *system or user*; it does not provide an inventory
  of files or functions the diff already shows.

### The Published-Release Test

Long-running branches accumulate tactical decisions — renames,
refactors, attempts-then-reverts. When deciding what counts as
branch-internal, use trunk or the parent branch as the baseline — not
intermediate states inside the current branch. Ask:

> Did users of the most recently published release ever experience
> this old name, old behavior, or bug?

If the answer is **no**, it is branch-internal narrative. Move it to
the commit message and describe only the final state in the artifact.

**Keep in shipped artifacts:**
- Deprecations and migration guides for symbols that actually shipped.
- `### Fixes` entries for bugs that affected users of a published
  release.
- Comments explaining *why the current code looks this way*
  (invariants, platform quirks) that make sense to a reader who never
  saw the previous version.

### Cleanup in Hindsight

When applying these rules retroactively from inside a feature branch,
first establish scope by diffing against the parent branch (or trunk)
to identify which commits this branch actually introduced. Then:

- **In-branch commits:** Prompt the user with two options: `fixup!`
  commits with `git rebase --autosquash` to address each causal commit
  at its source, or a single cleanup commit at branch tip.
- **Trunk/Parent commits:** Default to leaving them alone. Act only on
  explicit user instruction. If the user opts in, fold the cleanup
  into a single commit at branch tip; do not rewrite shared history.
- **Scope guard:** If cleaning prior slop would touch a colleague's
  work or expand the branch beyond its stated goal, stay in lane:
  protect the current goal and leave prior slop alone.

### Change Discipline

- Make the smallest coherent change that solves the verified problem;
  keep unrelated cleanup out of it.
- Reuse an existing file, component, helper, API, or test before adding
  a new one. Modify in place when the change fits the file's
  responsibility.
- Keep new APIs private until a caller outside the module needs them.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized high-touch module — not
  for a single-use helper or a one-line re-export.

### Keep Instructions Lean

Treat this file like code and prune it.

- Delete a line whose removal would not cause a mistake.
- Move multi-step procedures into skills, path-specific rules into
  nested AGENTS.md files, and hard limits into hooks or CI.
- Keep only non-obvious, broadly applicable defaults here. Anything a
  reader can infer from the code, a manifest, or a linter does not
  belong.
