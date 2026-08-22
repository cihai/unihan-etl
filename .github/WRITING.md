# Writing

How this project writes prose, for humans and agents alike. It governs
`README.md`, `CHANGES`, release notes, commit messages, CLI help text, error
messages, docstrings, source comments, migration notes, and the pages under
`docs/` — every surface a reader reaches.

For environment setup, the gates, and pull request workflow, see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Voice

Three surfaces, one voice. A docstring says what a caller may rely on; a
`CHANGES` entry says what changed; prose says what happens. All three are
present tense, lead with the thing being described, and stop. Why it was built
that way belongs in the commit message, which is timestamped and attached to
the diff.

The most useful editing operation is deleting the introductory sentence.

Lead with verbs and name concrete things. Put identifiers in backticks. Prefer
short declarative sentences, one operational fact each. Do not explain Python
to Python developers; do explain this project's semantics.

Type annotations describe shape. Documentation describes meaning. A sentence
that restates a signature has said nothing.

Use MUST, SHOULD, and MAY only where the normative sense is meant. Say what
actually happens rather than that something is "supported".

| Instead of                       | Prefer                             |
| --------------------------------- | ----------------------------------- |
| "We added…"                      | "`Packager.export` now accepts…"    |
| "New and improved"               | "`unihan-etl search` now…"          |
| "powerful", "seamless"           | state the capability                |
| "easily", "simply", "just"       | omit                                |
| "simple", "obvious", "intuitive" | omit                                |
| "robust"                         | name the failure that is handled    |
| "comprehensive"                  | name what is covered                |
| "production-ready"               | state the guarantee                 |
| "optimized", "blazingly fast"    | give the magnitude                  |
| "various fixes"                  | name the components                 |
| "under the hood"                 | omit unless observable              |
| "please note that", "note that"  | state the fact                      |
| "leverage", "utilize"            | "use"                               |
| "delve into"                     | "read", or omit                     |
| "best practices"                 | name the practice                   |
| "in order to"                    | "to"                                |

## Who you are writing for

The default reader runs the `unihan-etl` CLI — `download`, `export`, `search`,
`fields`, `files` — to turn the UNIHAN database into CSV, JSON, or YAML they
can load elsewhere. They know their data problem — CJK characters, readings,
variants — but you cannot assume they know UNIHAN's internals: the ~90 `k*`
fields, per-field delimiter rules, or how expansion turns `gun3 hung1 zung1`
into a list. Serve them first.

A second, smaller reader writes Python: `Packager` and `Options` from the
library API, the expansion layer, or tests built on the pytest plugin's
`unihan_quick_*` / `unihan_full_*` fixtures. Serve them too, but mark their
material opt-in — "for the rarer cases", "advanced" — so the default reader
knows they can stop. Never make the common case pay a comprehension tax for
the advanced one.

Rules that follow:

- **Second person, present tense, active.** "You export the fields you need",
  not "Fields are exported". Address the reader who is doing the thing.
- **Concept before flags.** Open by saying what a command or option *is* and
  what it does for the reader. The flags — `-F`, `-f`, `--destination` — are
  the last detail they need, not the first. A page that opens with "pass these
  flags" has buried the idea under its mechanics.
- **Say when they can stop.** Lead with the default: a plain `unihan-etl
  export` works and the download is cached. Let a skimmer leave after one
  paragraph.
- **Lean on the pipeline.** The reader thinks download → extract → normalize →
  expand → export; reinforce that chain when explaining where an option takes
  effect. It is the mental model the whole tool hangs on.
- **Progressive disclosure.** Order by how many readers need it: the default
  export → the one option a few will tune (a format, a field list) →
  expansion and pruning → driving `Packager` from Python. Each step is for a
  smaller audience than the last.
- **Name the trade-off.** If a choice costs something — a full UNIHAN
  download, a flat CSV that cannot hold expanded multi-value fields,
  `--no-expand` leaving delimiters for the reader to parse — say so, and say
  what it buys. State it; do not sell it.
- **Frame by concept, not by mechanism.** Do not headline a feature by its
  flag in prose; that names the implementation surface, the reader's last
  concern. Name the concept. Flag spellings, defaults, and metavars belong in
  the argparse-generated reference on each CLI page, and only there.

## README

A README is the shortest path from "what is this?" to competent use, not the
project's autobiography.

The first sentence is a contract. It says what abstraction the reader has been
handed, concretely enough to tell this package apart from the neighbouring
one.

Get to a runnable command or snippet before anything the reader can skip. A
logo, a mission statement, a comparison matrix and three paragraphs of history
in front of the install line all cost the same thing.

State the minimum Python version and meaningful platform constraints in
prose, not only in badges. `requires-python` in `pyproject.toml` is the
authority; the README must agree with it.

Name the distribution, the import, and the executable separately wherever
they differ. That distinction prevents a Python-specific class of confusion.

Examples are executable, not illustrative fiction. Never `unihan-etl
<some-options>`. See
[Documented examples that run](#documented-examples-that-run) for which
blocks are executed and how to write one that qualifies.

Document the semantic model, not the flag list. `--help` already enumerates
flags; what it cannot say is precedence, filesystem effects, what goes to
stdout versus stderr, and what a non-zero exit means.

State defaults explicitly — defaults are API. State negative guarantees where
they exist. Headings stay conventional and stable, because people deep-link
them. Badges are few and load-bearing.

## Documented examples that run

Examples in this repository are tests. This section is the contract for
writing one the test suite can actually see.

**A fence tag is cosmetic. Only a `>>> ` prompt executes.** A block written as

    ```python
    pkgr = Packager()
    ```

is prose that looks like a test. Nothing collects it, nothing runs it, and it
can be wrong for years. The same block written with prompts is a test:

    ```python
    >>> pkgr = Packager()
    ```

This is the single most expensive mistake available when editing
documentation, because removing the prompts leaves a green test suite and a
silently deleted test. When editing a file that contains examples, count the
prompts before and after: `rg -c '^\s*>>> ' README.md`.

**The fence tag is `python`.** Not `pycon`, not bare.

**Where examples run, in this repository specifically.** `addopts` in
`pyproject.toml` includes `--doctest-docutils-modules` and `-p no:doctest`:
the docutils-aware collector comes from
[gp-libs](https://gp-libs.git-pull.com)'s `pytest_doctest_docutils` plugin,
and `-p no:doctest` turns off pytest's own doctest plugin so only that
collector runs. `testpaths` lists `src/unihan_etl`, `tests`, `docs`, and
`README.md`. A `>>> ` block under any of those paths — a docstring, a page
under `docs/`, or `README.md` — is collected and executed by `pytest`.
`doctest_optionflags` enables `ELLIPSIS` and `NORMALIZE_WHITESPACE` globally.

The root `conftest.py` adds one name to `doctest_namespace`: `request`, and
only when the collected item is a doctest and `tmux` is on `PATH`. From
`request`, call `request.getfixturevalue("unihan_quick_options")` or another
pytest-plugin fixture name (`unihan_quick_packager`, `unihan_full_options`,
…) to pull a ready-made `Options` or `Packager` instead of downloading
UNIHAN live. Prefer the quick dataset — a small synthetic subset — to keep a
doctest fast and network-free. No other name is injected; anything else a
block uses must be imported in that block.

**`# doctest: +SKIP` is not permitted.** It is a workaround that tests
nothing. Use the fixtures.

**Do not downgrade a doctest to a non-executed block to make it pass.** A
`.. code-block::` or an unprompted fence does not run. If an example cannot
pass, fix the example or fix the code.

**Docstring examples** use the NumPy `Examples` section:

    Examples
    --------
    >>> from unihan_etl.cli._output import OutputFormat
    >>> OutputFormat.JSON.value
    'json'

**Room to grow.** The docutils collector reads `.md` and `.rst` whenever it
is loaded, which is everywhere in this repository. A prompted block added to
a documentation page is executed from that moment with no configuration
change. The MyST `{doctest}` directive and the reStructuredText `.. doctest::`
directive are available if a case ever needs an explicitly marked block.

## CLI help text and error messages

`unihan-etl`'s parser (`src/unihan_etl/cli/__init__.py`) uses a themed
`argparse` formatter (`create_themed_formatter`) built on Python's native
color theming: colors follow TTY detection and respect `NO_COLOR` and
`FORCE_COLOR`, matching `ColorMode.AUTO` / `ALWAYS` / `NEVER` in
`cli/_colors.py`. The top-level description carries an `examples:` block
(`build_description`) — one command per line, grouped under short category
labels (`download`, `explore`, …) — so `--help` shows working invocations,
not just a flag inventory. Follow that shape when adding a subcommand: a
one-line description, then an examples group if the command has more than
one common invocation.

Two layers handle failure, and they behave differently on purpose:

- **A subcommand's `command_*` function** (`cli/search.py`,
  `cli/export.py`, `cli/download.py`) catches `Exception` broadly, calls
  `log.exception(...)` first so the traceback lands in the log, prints
  `Error: <message>` to stderr, and returns a non-zero `int` exit code —
  never raises past its own boundary.
- **`Packager.from_cli`**, the library's own CLI boundary, also catches
  `Exception` broadly but skips `log.exception(...)` and calls
  `sys.exit(str(e))` directly: one line to stderr, no traceback logged.

Both layers catch broadly on purpose. `ruff`'s `BLE001` (blind-except)
exempts a broad catch that logs through `log.exception`, so the three
`command_*` functions need no per-file ignore; `Packager.from_cli` skips
that log call, so `BLE001` would flag it — `ruff`'s per-file-ignores
disables `BLE001` for `src/unihan_etl/core.py` for exactly that reason.

Raise `FieldNotFound` or `FileNotSupported` (`core.py`) for a bad field or
input file, not a bare `KeyError` or `ValueError`, so the CLI boundary can
turn it into a one-line message. `ruff`'s `EM` (flake8-errmsg) rule requires
assigning the message to a variable before raising:

```python
msg = f"Unknown field: {field}"
raise FieldNotFound(msg)
```

## The changelog

`CHANGES` is the changelog, rendered as the project's changelog page. It is
scanned, not read start to finish — the question a reader is asking is
whether an entry affects them. Modeled on Django's release-notes shape:
deliverables get titles and prose, not bullets.

**Release entry boilerplate.** Every release header is
`## unihan-etl X.Y.Z (YYYY-MM-DD)`. The file opens with a
`## unihan-etl X.Y.Z (unreleased)` placeholder block fenced by
`<!-- KEEP THIS PLACEHOLDER ... -->` and `<!-- END PLACEHOLDER ... -->` HTML
comments. Never delete either marker. New release entries land immediately
below the END marker, never above it.

**Open with a multi-sentence lead paragraph.** Plain prose, no italic. Open
with the version as sentence subject ("unihan-etl X.Y.Z ships …") so the
lead is self-contained when excerpted. Two to four sentences on what shipped
and who cares — user-visible takeaways, not internal mechanism.
Cross-reference detail docs with `{ref}` to keep the lead compact.

**Unreleased entries carry no lead paragraph and no version summary.**
Sections only (`### Breaking changes`, `### What's new` deliverables,
`### Fixes`, …). Speaking for a release — what the version "is", "ships", or
"focuses on" — is presumptuous before its scope is final; only the person
cutting the release writes that, and only when the release is actually
happening. Never write or edit a lead paragraph from a feature branch, and
never ask or imply that a release should happen.

**Each deliverable is a section, not a bullet.** Inside `### What's new`,
every distinct deliverable gets a `#### Deliverable title (#NN)` heading
naming it in user vocabulary, followed by 1-3 prose paragraphs explaining
what shipped. Do not wrap a paragraph in `- ` — bullets are for enumerable
lists, not paragraph containers. Cross-link detail docs
(`See {ref}\`foo\` for details.`) so prose stays focused.

**The deliverable test.** Before writing an entry, ask: "What's the
deliverable, in user vocabulary?" If that cannot be answered in one
sentence, the entry is not ready. Mechanism — helper internals, byte
counters, schema-validation locations — belongs in pull request
descriptions and code comments, not the changelog.

**Fixed subheadings**, in this order when present: `### Breaking changes`,
`### Dependencies`, `### What's new`, `### Fixes`, `### Documentation`,
`### Development`. Dev tooling (helper scripts, internal automation) lives
under `### Development`. For breaking changes, show the migration path with
concrete inline code (a `# Before` / `# After` fenced block). Dependency
floor bumps use the form `` Minimum `pkg>=X.Y.Z` (was `>=X.Y.W`) ``.

**PR refs `(#NN)`** sit in each deliverable's `####` heading.

**When bullets are appropriate.** Catch-all sections (`### Fixes`,
occasionally `### Documentation`) with 3+ genuinely small items use bullets —
one line each, never paragraphs. If a bullet swells past two lines, promote
it to a `#### Title (#NN)` heading with prose body.

**Anti-patterns.** Fragile metrics — token ceilings, third-party version
pins, percent benchmarks, exact byte counts — describe the capability, not
the math. Private symbols and internal jargon. Walls of text dressed up as
bullets. Breaking changes buried mid-entry instead of given their own
subheading at the top.

**Always link autodoc'd APIs.** Any class, method, function, exception, or
attribute with its own rendered page must be cited via the matching role —
never plain backticks. Doc pages without explicit ref labels use `{doc}`.
Plain backticks are correct for code syntax, env vars, parameter names, and
file paths that are not doc pages.

**MyST roles.** Classes use `{class}`, methods `{meth}`, functions `{func}`,
exceptions `{exc}`, attributes `{attr}`, internal anchors `{ref}`, doc-path
links `{doc}`.

**Summarization style.** When asked "what changed in the latest version?" or
similar, lead with the entry's lead paragraph (paraphrased if needed),
followed by each `####` deliverable heading under `### What's new` with a
one-sentence summary. Cite `(#NN)` only if asked for source links. Do not
invent versions, dates, or numbers not present in `CHANGES`. Do not quote
line numbers or file offsets — those shift as the file evolves.

## Release notes

`CHANGES` is the permanent ledger; a release page is editorial. Lead with one
paragraph naming the headline change, then three to five highlights, then
link the full changelog.

Numbers over adjectives. "Cold start 41 ms to 6 ms" is a sentence; "much
faster startup" is a smell.

A list of merged commit subjects is a merge log wearing a release-note hat.
Put the hand-written highlights above it.

Versions are PEP 440 identifiers. Semantic-versioning meaning is applied to
the documented public API — which includes command names, options, exit
statuses, configuration keys, environment variables, and serialized formats,
not only imported Python symbols.

## Docstrings

The prime directive: never restate the type. The annotation is the source of
truth; the docstring carries what the annotation cannot.

This is documentation debt wearing a docstring:

    def get_char(pkgr: Packager) -> str:
        """Get the character.

        Parameters
        ----------
        pkgr : Packager
            The packager.

        Returns
        -------
        str
            The character.
        """

Document instead the dimensions the type system cannot encode: mutation,
ownership, ordering, timing, failure, idempotence, concurrency, units and
ranges, boundary behaviour, platform differences, and security boundaries.

**Classes with fields** — `NamedTuple`, dataclasses — document every field in
an `Attributes` section:

```python
class _ColorizedLine(t.NamedTuple):
    """Result of colorizing an example line.

    Attributes
    ----------
    text : str
        Colorized line content.
    expect_value : bool
        Whether the next token is a value for the preceding option.
    """
```

Autodoc renders every field whether or not you describe it, so an
undocumented `NamedTuple` field ships to the API docs as "Alias for field
number 0" and a dataclass field ships bare. Document all of them — a class
with three fields and two documented still ships a stub for the third.

The ambiguity worth resolving by example: whether "retry three times" means
three attempts or four. State it.

The first sentence stands alone; tooling truncates there. PEP 257 applies:
triple double quotes, an imperative one-line summary ending in a period, a
blank line before any extended description. Do not repeat an introspectable
signature.

NumPy-style docstrings in reStructuredText are this repository's one
dialect, enforced by `ruff`'s `pydocstyle` convention (`convention = "numpy"`
in `pyproject.toml`) rather than relitigated in review.

## Source comments

A comment ships only if it passes all three gates. Fail any: delete or
rewrite. Borderline: delete — borderline means the information is
reconstructible, which is what makes deletion cheap.

**Loss.** Three years from now, would losing this cost a maintainer real time
rediscovering intent, an invariant, a constraint, or a failure mode the code
and tests do not already make obvious?

**Elite.** Would SQLite, Redis, the Go standard library, or CPython write
this comment, at this length? Those projects state the constraint and stop.
They do not argue with an imagined objector.

**Upkeep.** Will it stay true without maintenance? A comment that hand-syncs
a value the code owns — a count, an offset, a line reference, a duplicated
constant — is false the first time that value moves.

### Ceiling

One or two lines. A comment reaching four is either carrying several facts,
in which case split it, or arguing, in which case cut it to the fact.

Rationale, alternatives weighed, and the story of how the code got here
belong in the commit message: timestamped, attached to the exact diff, and
free to maintain.

### Keep

- Why over how: upstream quirks, protocol and compatibility constraints,
  performance tradeoffs still part of the contract.
- Invariants, preconditions, ordering, lifetime, and concurrency requirements
  that types and tests cannot express.
- Code that looks wrong but is not, so a later cleanup does not reintroduce
  the bug.
- A high-level sketch of an algorithm whose local operations do not reveal
  the whole.

### Delete

- Narration of the next lines; code translated into English.
- Restated names, types, defaults, or control flow.
- Values duplicated from the code and hand-synced.
- Justification, hedging, or apology for a choice.
- Speculation about future requirements.
- History version control already holds, including commented-out code.
- Ticket and issue numbers. They say nothing to a reader without tracker
  access, and they rot when the tracker moves.
- Transient observations — "currently", "for now", "the latest release" —
  that go stale with no nearby edit.

### The upkeep gate in practice

It reaches values that track our own code. It does not reach frozen external
facts.

Bad (Delete):

    # There are 321 tests to complete for servers.

Good (Keep):

    # CPython < 3.11 has no ExceptionGroup, so this branch stays.

### Documentation exception

Doctests, minimal usage examples, and NumPy-style `Parameters`, `Returns`,
`Attributes`, and `Raises` entries on public API are exempt from the loss
gate — they serve the caller, not the maintainer, and a doctest that runs is
also a test. They are exempt from nothing else. Ceiling: a good man page
entry.

## Cross-references

Point the advanced reader at the deep-dive rather than inlining it, and put
the link where their interest peaks — on the phrase that made them curious
("drive the pipeline from Python") — not as a standalone footnote the eye
skips. A `{ref}` must match its target's anchor exactly — anchors in this
repository are lowercase and hyphenated (`cli-export`,
`developmental-releases`). `just build-docs` catches a broken
cross-reference; the doctests do not — build the docs before shipping a docs
change.

Link the first prose mention of any symbol that has a useful destination on
that page: Python objects, unihan-etl APIs, CLI command pages, topic pages,
external tools or projects. Use the most specific target: `{class}`,
`{meth}`, `{func}`, `{mod}`, `{exc}`, `{attr}` for API objects; `{ref}` or
`{doc}` for documentation pages and anchors; a Markdown link for external
projects. After the first linked mention on a page, later mentions can stay
plain unless distance or context makes another link useful.

Do not rely on a later reference section to satisfy the first-mention rule.
If the first occurrence would be a heading, grid-card teaser, or
introductory sentence, link that occurrence or retitle the heading so the
first prose mention can carry the link. Leave command examples, code
blocks, and literal configuration values as code; link the surrounding
prose instead.

**What stays precise.** Warm the framing, never the facts. Field tables,
delimiter rules, verbatim UNIHAN records (`U+3400  kDefinition  …`), exact
error strings, bibliographies, and class or function cross-references carry
meaning in their exact form — leave them alone. The friendly voice belongs
in the sentences *around* a precise block, not inside it paraphrasing it
into vagueness. `docs/topics/unihan.md` is the worked example: it says what
UNIHAN *is* and why it matters before any tooling appears, then earns the
tool's existence by quoting real records to show why a flat CSV cannot hold
them.

**Reference pages** follow two mechanical conventions, separate from voice:

- **CLI pages** (`docs/cli/*.md`) share one shape: an anchor, a one-sentence
  description, a `## Command` section whose `{eval-rst}` block wraps
  `.. argparse::`, then `## Examples` as `console` blocks. The argparse
  block owns the flag inventory; keep prose out of it.
- **API pages** (`docs/api/*.md`, `docs/internals/api/*.md`) wrap
  `.. automodule:: <module>` with `:members:` in `{eval-rst}`. Voice work
  happens in the module docstrings, not the page shell.

Before shipping a page under `docs/`: does it open with what the feature
*is* rather than how to invoke it? Can a reader who needs only the default
export stop after the first paragraph? Is anything framed by its flag that
should be named by concept? Are the Python-only and advanced parts clearly
marked opt-in? Do the doctests run, and did every record, table, error
string, and cross-reference stay exact?

## Terminology and capitalization

Pick the domain noun and keep it. Say "field" for a `k*` UNIHAN attribute
throughout, not "attribute" in one paragraph and "column" in the next. Say
"expand" for turning a delimited value into a structured list or dict, and
"prune" for dropping empty values — those are the pipeline's own verb
choices (`expansion.py`, `Options.expand`, `Options.prune_empty`); do not
substitute "parse" or "clean". Write "UNIHAN" (all caps), matching Unicode's
own name for the database, everywhere except inside a literal field name
(`kDefinition`) or file path.

Stable vocabulary is what makes search, deep links, and an agent's retrieval
work at all.

Python and PyPI keep their own capitalisation. Distribution names are
written as they are published.

Do not write counts into prose — how many fields exist, how many tests there
are. They go stale silently and no reader needs them. Counts that pin a
fixture or guard an invariant are different, and belong in code.

## Markdown

Prose wraps at 80 columns. Table rows, badge lines, and long links are
exempt, because breaking them harms rendering. A pull request or issue body
does not wrap at all: GitHub renders a single newline as a space in a file
and as a line break in a comment, so a wrapped comment body arrives as
ragged stubs.

GitHub alert blocks — `> [!NOTE]`, `> [!WARNING]` — render as literal text
outside GitHub, so reserve them for at most one load-bearing warning per
document.

Do not use a local absolute path or an email address in anything published.

## Code blocks

Code blocks are paste-and-run units: pasting one block runs exactly one
intended action. Executed examples are exempt — the test suite runs them,
nobody pastes them.

- **One command per block.** Multiple steps may share a block only when
  explicitly chained with `&&`, `;`, or `\` continuations — the chain is
  then one logical command.
- **Explanations go in prose above the block**, never as `#` comments inside
  it.
- **Command menus are per-command blocks with prose lead-ins**, not tables.
- **Shell commands use the `console` tag with a `$ ` prefix.**
- **Split long commands with `\`** — one flag or flag+value pair per
  indented continuation line, positional arguments last.

Good — show the last ten commits as a graph:

```console
$ git log \
    --max-count=10 \
    --graph \
    --oneline
```

Bad:

```console
# Show the last ten commits as a graph
$ git log --max-count=10 --graph --oneline
```

## Commits

```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.

what:
- Specific technical changes made
- Focused on a single topic
```

Keep the subject to 50 characters or fewer, excluding any trailing `(#NN)`
pull request reference, and wrap body lines at 72. Separate the `why:` and
`what:` blocks with a blank line.

Routine maintenance commits drop the colon and take a capitalised
description, which is what distinguishes them at a glance in
`git log --oneline`:

```
py(deps[dev]) Bump dev packages
ai(rules[AGENTS]) Judge comments by three gates
```

Everything that changes behaviour keeps the colon.

Common types:

- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **ci**: Workflow and pipeline changes
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (`CLAUDE.md`)
- **ai(claude[command])**: Claude Code command changes

Example:

```
Packager(fix[export]): Handle empty fields

why: An empty field left a stray delimiter in the CSV output.

what:
- Skip a field when every value in it is empty
- Add a regression test with an all-empty kDefinition
```

For a multi-line message, use a heredoc so the formatting survives:

```console
$ git commit -m "$(cat <<'EOF'
Scope(feat[detail]): Concise description

why: Explanation of the change.

what:
- First change
- Second change
EOF
)"
```

### Release commits

Never create tags. Never push tags. The owner handles tagging and tag pushes,
because a tag triggers the publish workflow.

A release commit subject is plain and short: `Tag v<version>`. The detailed
why and what go in the body. Do not use the `Scope(type[detail]):` format
for a release — it buries the lede.

## Slop prevention

Treat AI slop as review-hostile noise, not as proof that text or code is
wrong. The goal is to maximise information density.

- **AI signatures.** No "Generated by", no conversational filler, no
  unexplained emoji, no tool metadata.
- **Brittle references.** No hard-coded line numbers, fragile file counts,
  dated "as of" claims, bare SHAs, or local absolute paths — unless they are
  strict evidentiary artefacts such as a benchmark log.
- **Diff narration.** Do not restate what moved, was renamed, or was removed
  in anything the reader holds alongside the diff: code, docstrings, README,
  or a pull request description. The diff and the commit message already
  carry it.
- **Branch-internal narrative.** Do not mention intermediate states,
  abandoned approaches, or "no longer" behaviour unless users of a published
  release actually experienced the old state.
- **Low-value scaffolding.** No ownerless TODOs, unused future-proofing,
  debug artefacts, or defensive wrappers around failure modes nothing can
  reach.
- **Prose inflation.** The diction table under [Voice](#voice) governs;
  replace an inflated word with a concrete description of behaviour,
  constraints, or trade-offs.
- **Coded labels.** Write rules and findings as plain imperatives. No `[R1]`,
  `Option B`, or any index a reader has to decode.

**Durable source links.** Link to a pinned revision, never to trunk.
`blob/master/…` rots silently — the file moves, lines shift, and the anchor
lands on unrelated code while still resolving.

- Prefer a release tag (`blob/v0.43.0/…`). Most durable, and it tells the
  reader which released version the claim held for.
- Otherwise use a 7-char commit ref (`blob/9a29b1a/…`) reachable from
  trunk. Use when there is no tag or the claim is about unreleased code.
  Never a PR-head SHA — it can be rebased or garbage-collected.
- Reserve `blob/master/…` for living documents meant to always show the
  latest state, such as a contributing guide.
- Line anchors (`#L120-L145`) are only safe on a pinned ref.

Preserve the "why". Never delete a comment documenting an invariant, a
protocol constraint, a platform quirk, or an upstream workaround — those are
the facts [Source comments](#source-comments) keeps, and every other comment
is judged by it.
