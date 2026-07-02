# Documentation voice

This file covers the *voice* of prose under `docs/` — how to frame a
page so a reader meets the idea before its flags. It complements the
repository-root `AGENTS.md`, which already governs code blocks,
shell-command formatting, changelog conventions, and MyST roles. When
the two overlap, the root file wins; this one only answers the
question it leaves open: how should the prose sound?

## Who you are writing for

The default reader runs the `unihan-etl` CLI — `download`, `search`,
`export` — to turn the UNIHAN database into CSV, JSON, or YAML they
can load somewhere else. They know their data problem — CJK
characters, readings, variants — but you cannot assume they know
UNIHAN's internals: the 90-odd `k*` fields, per-field delimiter
rules, or how expansion turns `gun3 hung1 zung1` into a list.

A second, smaller reader writes Python: `Packager` and `Options`
from the library API, the expansion layer, or tests built on the
pytest plugin's `unihan_quick_*` / `unihan_full_*` fixtures. Serve
them too, but mark their material opt-in ("for the rarer cases",
"advanced") so the default reader knows they can stop. Never make
the common case pay a comprehension tax for the advanced one.

## Voice

- **Second person, present tense, active.** "You export the fields
  you need", not "Fields are exported". Address the reader who is
  doing the thing.
- **Concept before configuration.** Open by saying what the command
  or option *is* and what it does for the reader. The flags — `-F`,
  `-f`, `--destination` — are the last detail they need, not the
  first. A page that opens with "pass these flags" has buried the
  idea under its mechanics.
- **Say when they can stop.** Lead with the default: a plain
  `unihan-etl export` works and the download is cached. Let a
  skimmer leave after one paragraph.
- **Lean on the pipeline.** The reader thinks download → extract →
  normalize → expand → export; reinforce that chain when you explain
  where an option takes effect. It is the mental model the whole
  tool hangs on.
- **Progressive disclosure.** Order by how many readers need it: the
  default export → the one option a few will tune (a format, a field
  list) → expansion and pruning → driving `Packager` from Python.
  Each step is for a smaller audience than the last.
- **Name the trade-off.** If a choice costs something — a full
  UNIHAN download, a flat CSV that cannot hold expanded multi-value
  fields, `--no-expand` leaving delimiters for the reader to parse —
  say so, and say what it buys. State it; don't sell it.
- **Frame by concept, not by mechanism.** Don't headline a feature
  by its flag in prose; that names the implementation surface, the
  reader's last concern. Name the concept. The mechanics vocabulary
  — flag spellings, defaults, metavars — belongs in the
  argparse-generated reference on each CLI page, and only there.

## Examples that run

Prose examples under `docs/` are doctests — `testpaths` includes
`docs` and `README.md`, and `--doctest-docutils-modules` executes
every fenced `>>>` block under pytest.

- Fence a `>>>` session as a ```` ```python ```` block; `ELLIPSIS`
  and `NORMALIZE_WHITESPACE` are on via `doctest_optionflags`, so
  `...` output just works. Use a ```` ```console ```` block with a
  `$` prompt for shell commands — those are not executed.
- The root `conftest.py` adds `request` to `doctest_namespace`;
  `request.getfixturevalue()` can pull the pytest plugin's fixtures
  (`unihan_quick_options`, `unihan_quick_packager`, …) instead of
  downloading UNIHAN live. Prefer the quick dataset — a small
  synthetic subset — to keep a docs doctest fast and network-free.

## What stays precise

Warm the framing, never the facts. Field tables, delimiter rules,
verbatim UNIHAN records (`U+3400  kDefinition  …`), exact error
strings, bibliographies, and class or function cross-references carry
meaning in their exact form — leave them alone. The friendly voice
belongs in the sentences *around* a precise block, not inside it
paraphrasing it into vagueness.

## Cross-references

Point the advanced reader at the deep-dive rather than inlining it,
and put the link where their interest peaks — on the phrase that
made them curious ("drive the pipeline from Python") — not as a
standalone footnote the eye skips. Use the MyST roles listed in the
root `AGENTS.md`. A `{ref}` must match its target's anchor exactly —
anchors here are lowercase and hyphenated (`cli-export`,
`developmental-releases`). `just build-docs` catches a broken
cross-reference; the doctests do not — so build the docs first.

Link the first prose mention of any symbol that has a useful
destination on that page. This includes Python objects, unihan-etl
APIs, CLI command pages, topic pages, and external tools or projects.
Use the most specific target available: `{class}`, `{meth}`,
`{func}`, `{mod}`, `{exc}`, or `{attr}` for API objects; `{ref}` or
`{doc}` for documentation pages and section anchors; and a Markdown
link or reference link for external projects. After the first linked
mention on a page, later mentions can stay plain unless the distance
or context makes another link useful.

Do not rely on a later reference section to satisfy the first-mention
rule. If the first occurrence would be a heading, grid-card teaser,
or introductory sentence, link that occurrence or retitle the heading
so the first prose mention can carry the link. Leave command
examples, code blocks, and literal configuration values as code; link
the surrounding prose instead.

## A page that does this

`docs/topics/unihan.md` is the worked example: it says what UNIHAN
*is* and why it matters before any tooling appears, then earns the
tool's existence in "The problem" — real records (`kDefinition`,
`kCantonese`, `kHanyuPinyin`) quoted verbatim to show why a flat CSV
cannot hold them and why expansion must stay configurable. Records
and bibliographies stay exact; the surrounding prose does the
framing. Read it before reshaping another page.

## Reference pages

Two mechanical conventions, separate from voice:

- **CLI pages** (`docs/cli/*.md`) share one shape: an anchor, a
  one-sentence description, a `## Command` section whose `{eval-rst}`
  block wraps `.. argparse::`, then `## Examples` as `console`
  blocks. The argparse block owns the flag inventory; keep prose out.
- **API pages** (`docs/api/*.md`, `docs/internals/api/*.md`) wrap
  `.. automodule:: <module>` with `:members:` in `{eval-rst}`. Voice
  work happens in the module docstrings, not the page shell.

## Before you commit

- Does the page open with what the feature *is*, or how to invoke it?
- Can a reader who needs only the default export stop after the
  first paragraph?
- Is anything framed by its flag that should be named by concept?
- Are the Python-only and advanced parts clearly marked opt-in?
- Do the doctests run (`just test`), and did you leave every record,
  table, error string, and cross-reference exact?
- Did `just build-docs` stay clean — no new warning, no broken
  cross-reference?
