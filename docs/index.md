(index)=

# unihan-etl

Download, search, and export Unicode's UNIHAN CJK character dataset. Normalizes raw Unicode data files into clean JSON, CSV, or YAML.

unihan-etl handles the data pipeline. For SQLAlchemy models, see [unihan-db](https://unihan-db.git-pull.com/). For end-user character lookups, see [cihai](https://cihai.git-pull.com/).

::::{grid} 1 2 3 3
:gutter: 2 2 3 3

:::{grid-item-card} Quickstart
:link: quickstart
:link-type: doc
Install and run your first export.
:::

:::{grid-item-card} CLI Reference
:link: cli/index
:link-type: doc
Every command, flag, and option.
:::

:::{grid-item-card} API Reference
:link: api/index
:link-type: doc
Core modules, types, and pytest plugin.
:::

::::

::::{grid} 1 1 2 2
:gutter: 2 2 3 3

:::{grid-item-card} Topics
:link: topics/index
:link-type: doc
About UNIHAN, FAQ, and data format details.
:::

:::{grid-item-card} Contributing
:link: project/index
:link-type: doc
Development setup, code style, and release process.
:::

::::

## Install

```console
$ uv tool install unihan-etl
```

```console
$ pip install unihan-etl
```

## At a glance

Fetches raw UNIHAN data from unicode.org.

```console
$ unihan-etl download
```

Look up a character across all fields.

```console
$ unihan-etl search 好
```

Export the full dataset to JSON (also supports CSV, YAML).

```console
$ unihan-etl export -F json
```

```{toctree}
:hidden:

quickstart
cli/index
api/index
topics/index
internals/index
project/index
history
```

```{toctree}
:hidden:
:caption: More

migration
```
