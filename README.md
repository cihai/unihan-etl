# unihan-etl &middot; [![Python Package](https://img.shields.io/pypi/v/unihan-etl.svg)](https://pypi.org/project/unihan-etl/) [![License](https://img.shields.io/github/license/cihai/unihan-etl.svg)](https://github.com/cihai/unihan-etl/blob/master/LICENSE) [![Code Coverage](https://codecov.io/gh/cihai/unihan-etl/branch/master/graph/badge.svg)](https://codecov.io/gh/cihai/unihan-etl)

An [ETL][etl] tool for the Unicode Han Unification ([UNIHAN](http://www.unicode.org/charts/unihan.html)) database
releases: unihan-etl downloads, unpacks, and converts Unicode's raw CJK character data files into a flattened,
tabular export or a structured, hierarchical one.

unihan-etl serves dual purposes: a typed Python library offering an [API](https://unihan-etl.git-pull.com/en/latest/)
for working with the data as Python objects, and a [CLI](https://unihan-etl.git-pull.com/en/latest/cli.html) for
exporting to CSV, JSON, or YAML.

unihan-etl is a component of the [cihai](https://cihai.git-pull.com) suite of CJK related projects. For a similar
tool, see [libUnihan](http://libunihan.sourceforge.net/).

As of v0.31.0, unihan-etl is compatible with UNIHAN Version 15.1.0 ([released on 2023-09-01, revision 35](https://www.unicode.org/reports/tr38/tr38-35.html#History)).

## The UNIHAN database

The UNIHAN database spreads its data across multiple files. A sample:

```tsv
U+3400	kCantonese		jau1
U+3400	kDefinition		(same as U+4E18 丘) hillock or mound
U+3400	kMandarin		qiū
U+3401	kCantonese		tim2
U+3401	kDefinition		to lick; to taste, a mat, bamboo bark
U+3401	kHanyuPinyin		10019.020:tiàn
U+3401	kMandarin		tiàn
```

Field values vary in shape by field type.
[kHanyuPinyin](http://www.unicode.org/reports/tr38/#kHanyuPinyin) maps a codepoint to an entry in
[Hànyǔ Dà Zìdiǎn](https://en.wikipedia.org/wiki/Hanyu_Da_Zidian); `10019.020:tiàn` is one such entry.
Some fields hold several:

```tsv
U+5EFE	kHanyuPinyin		10513.110,10514.010,10514.020:gǒng
U+5364	kHanyuPinyin		10093.130:xī,lǔ 74609.020:lǔ,xī
```

`kHanyuPinyin` delimits multiple entries with spaces, separates a location from its pinyin reading
with `:`, and separates multiple locations or readings with `,`. This is one of 90 fields in the
database.

[etl]: https://en.wikipedia.org/wiki/Extract,_transform,_load

## Tabular, "Flat" output

### CSV (default)

```console
$ unihan-etl
```

```csv
char,ucn,kCantonese,kDefinition,kHanyuPinyin,kMandarin
㐀,U+3400,jau1,(same as U+4E18 丘) hillock or mound,,qiū
㐁,U+3401,tim2,"to lick; to taste, a mat, bamboo bark",10019.020:tiàn,tiàn
```

With `$ unihan-etl -F yaml --no-expand`:

```yaml
- char: 㐀
  kCantonese: jau1
  kDefinition: (same as U+4E18 丘) hillock or mound
  kHanyuPinyin: null
  kMandarin: qiū
  ucn: U+3400
- char: 㐁
  kCantonese: tim2
  kDefinition: to lick; to taste, a mat, bamboo bark
  kHanyuPinyin: 10019.020:tiàn
  kMandarin: tiàn
  ucn: U+3401
```

To preview in the CLI, try [tabview](https://github.com/TabViewer/tabview) or
[csvlens](https://github.com/YS-L/csvlens).

### JSON

```console
$ unihan-etl -F json --no-expand
```

```json
[
  {
    "char": "㐀",
    "ucn": "U+3400",
    "kDefinition": "(same as U+4E18 丘) hillock or mound",
    "kCantonese": "jau1",
    "kHanyuPinyin": null,
    "kMandarin": "qiū"
  },
  {
    "char": "㐁",
    "ucn": "U+3401",
    "kDefinition": "to lick; to taste, a mat, bamboo bark",
    "kCantonese": "tim2",
    "kHanyuPinyin": "10019.020:tiàn",
    "kMandarin": "tiàn"
  }
]
```

Tools:

- View in CLI: [python-fx](https://github.com/cielong/pyfx),
  [jless](https://github.com/PaulJuliusMartinez/jless) or
  [fx](https://github.com/antonmedv/fx).
- Filter via CLI: [jq](https://github.com/stedolan/jq),
  [jql](https://github.com/yamafaktory/jql),
  [gojq](https://github.com/itchyny/gojq).

### YAML

```console
$ unihan-etl -F yaml --no-expand
```

```yaml
- char: 㐀
  kCantonese: jau1
  kDefinition: (same as U+4E18 丘) hillock or mound
  kHanyuPinyin: null
  kMandarin: qiū
  ucn: U+3400
- char: 㐁
  kCantonese: tim2
  kDefinition: to lick; to taste, a mat, bamboo bark
  kHanyuPinyin: 10019.020:tiàn
  kMandarin: tiàn
  ucn: U+3401
```

Filter via the CLI with [yq](https://github.com/mikefarah/yq).

## "Structured" output

A codepoint can carry more structure than a flat row holds. unihan-etl extracts it uniformly and
prunes empty values, exporting to JSON, YAML, and Python list/dicts.

<div class="admonition">

Why not CSV?

CSV only holds table-like data. JSON and YAML also hold key-values and hierarchical entries.

</div>

### JSON

```console
$ unihan-etl -F json
```

```json
[
  {
    "char": "㐀",
    "ucn": "U+3400",
    "kDefinition": ["(same as U+4E18 丘) hillock or mound"],
    "kCantonese": ["jau1"],
    "kMandarin": {
      "zh-Hans": "qiū",
      "zh-Hant": "qiū"
    }
  },
  {
    "char": "㐁",
    "ucn": "U+3401",
    "kDefinition": ["to lick", "to taste, a mat, bamboo bark"],
    "kCantonese": ["tim2"],
    "kHanyuPinyin": [
      {
        "locations": [
          {
            "volume": 1,
            "page": 19,
            "character": 2,
            "virtual": 0
          }
        ],
        "readings": ["tiàn"]
      }
    ],
    "kMandarin": {
      "zh-Hans": "tiàn",
      "zh-Hant": "tiàn"
    }
  }
]
```

### YAML

```console
$ unihan-etl -F yaml
```

```yaml
- char: 㐀
  kCantonese:
    - jau1
  kDefinition:
    - (same as U+4E18 丘) hillock or mound
  kMandarin:
    zh-Hans: qiū
    zh-Hant: qiū
  ucn: U+3400
- char: 㐁
  kCantonese:
    - tim2
  kDefinition:
    - to lick
    - to taste, a mat, bamboo bark
  kHanyuPinyin:
    - locations:
        - character: 2
          page: 19
          virtual: 0
          volume: 1
      readings:
        - tiàn
  kMandarin:
    zh-Hans: tiàn
    zh-Hant: tiàn
  ucn: U+3401
```

## Features

- downloads and caches UNIHAN releases from unicode.org
- follows the field semantics in
  [UNIHAN's database design](http://www.unicode.org/reports/tr38/)
- exports to CSV, JSON, and YAML (YAML requires [pyyaml](http://pyyaml.org/)) via `-F`
- exports a subset of fields via `-f`
- expands multi-value delimited fields into structured lists/dicts for YAML, JSON, and Python exports
- handles the Unicode-heavy encoding of UNIHAN's source files
- [data package](http://frictionlessdata.io/data-packages/) descriptor included
- core component and dependency of [cihai](https://cihai.git-pull.com), a CJK library
- Python 3.10+ and PyPy

If you encounter a problem or have a question, please
[create an issue](https://github.com/cihai/unihan-etl/issues/new).

## Installation

Using [uv](https://docs.astral.sh/uv/) to add the CLI to your project:

```console
$ uv add unihan-etl
```

Using [pip](https://pip.pypa.io/en/stable/):

```console
$ pip install --user unihan-etl
```

Run the tool without a persistent install via [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```console
$ uvx unihan-etl
```

or by [pipx](https://pypa.github.io/pipx/docs/):

```console
$ pipx install unihan-etl
```

### Developmental releases

Using [uv](https://docs.astral.sh/uv/getting-started/features/), opt-in to pre-release versions:

```console
$ uv add --prerelease=allow unihan-etl
```

To pin a specific pre-release (for example `0.27.0a1`):

```console
$ uv add --prerelease=allow 'unihan-etl==0.27.0a1'
```

[pip](https://pip.pypa.io/en/stable/):

```console
$ pip install --user --upgrade --pre unihan-etl
```

[pipx](https://pypa.github.io/pipx/docs/):

```console
$ pipx install --suffix=@next 'unihan-etl' --pip-args '\--pre' --force
```

This installs the pre-release under the `unihan-etl@next` executable name, alongside a regular
install. Run it the same way, for example `unihan-etl@next export`.

Run pre-release builds without installing with [`uvx`](https://docs.astral.sh/uv/guides/tools/):

```console
$ uvx --prerelease=allow unihan-etl
```

Or pinned to that example version:

```console
$ uvx --from 'unihan-etl==0.27.0a1' unihan-etl
```

Swap `0.27.0a1` for whichever pre-release you plan to use.

## Usage

Without `--destination`, an export writes to the platform's XDG data directory (see
[Code layout](#code-layout)) and the download is cached, so a repeat run skips the network. A failed
export exits non-zero with a one-line message on stderr rather than a traceback. See
[unihan-etl CLI arguments](https://unihan-etl.git-pull.com/en/latest/cli.html) for every flag,
including how to specify columns, files, and download URLs.

To output CSV, the default format:

```console
$ unihan-etl
```

To output JSON:

```console
$ unihan-etl -F json
```

To output YAML:

Add PyYAML with uv:

```console
$ uv add pyyaml
```

Or install it with pip:

```console
$ pip install --user pyyaml
```

Then run:

```console
$ unihan-etl -F yaml
```

To only output the kDefinition field in a csv:

```console
$ unihan-etl -f kDefinition
```

To output multiple fields, separate with spaces:

```console
$ unihan-etl -f kCantonese kDefinition
```

To output to a custom file:

```console
$ unihan-etl --destination ./exported.csv
```

To output to a custom file (templated file extension):

```console
$ unihan-etl --destination ./exported.{ext}
```

See [unihan-etl CLI arguments](https://unihan-etl.git-pull.com/en/latest/cli.html) for advanced
usage examples.

## Code layout

```console
# cache dir (Unihan.zip is downloaded, contents extracted)
{XDG cache dir}/unihan_etl/

# output dir
{XDG data dir}/unihan_etl/
  unihan.json
  unihan.csv
  unihan.yaml   # (requires pyyaml)

# package dir
unihan_etl/
  core.py    # argparse, download, extract, transform UNIHAN's data
  options.py    # configuration object
  constants.py  # immutable data vars (field to filename mappings, etc)
  expansion.py  # extracting details baked inside of fields
  types.py      # type annotations
  util.py       # utility / helper functions

# test suite
tests/*
```

## API

unihan-etl is a typed Python library underneath the CLI; see the full [API].

```python
>>> from unihan_etl.core import Packager
>>> pkgr = Packager()
>>> hasattr(pkgr.options, 'destination')
True
```

[API]: https://unihan-etl.git-pull.com/en/latest/api.html

## Developing

```console
$ git clone https://github.com/cihai/unihan-etl.git
```

```console
$ cd unihan-etl
```

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for this repository's setup and gates.
[Bootstrap your environment and learn more about contributing](https://cihai.git-pull.com/contributing/)
to any cihai project: the suite shares `pytest`, `sphinx`, `mypy`, `ruff`, `tmuxp`, and file watcher
helpers (e.g. `entr(1)`) across repositories.

## More information

[![Docs](https://github.com/cihai/unihan-etl/workflows/docs/badge.svg)](https://unihan-etl.git-pull.com/)
[![Build Status](https://github.com/cihai/unihan-etl/workflows/tests/badge.svg)](https://github.com/cihai/unihan-etl/actions?query=workflow%3A%22tests%22)
