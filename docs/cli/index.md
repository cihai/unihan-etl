(cli)=

(commands)=

# CLI Reference

::::{grid} 1 1 2 2
:gutter: 2 2 3 3

:::{grid-item-card} unihan-etl download
:link: download
:link-type: doc
Download and cache the UNIHAN database.
:::

:::{grid-item-card} unihan-etl export
:link: export
:link-type: doc
Export UNIHAN data to CSV, JSON, or YAML.
:::

:::{grid-item-card} unihan-etl search
:link: search
:link-type: doc
Look up character data by codepoint or field.
:::

:::{grid-item-card} unihan-etl fields
:link: fields
:link-type: doc
List available UNIHAN fields.
:::

:::{grid-item-card} unihan-etl files
:link: files
:link-type: doc
List available UNIHAN source files.
:::

::::

```{toctree}
:caption: Data Operations
:maxdepth: 1

export
download
search
```

```{toctree}
:caption: Information
:maxdepth: 1

fields
files
```

(cli-main)=

## Main command

The `unihan-etl` command is the entry point for all UNIHAN ETL operations. Use subcommands to export data, download the database, or query fields and files.

### Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :nosubcommands:

    subparser_name : @replace
        See :ref:`cli-export`
```

## Global Options

- `-l, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Logging level (default: INFO)
- `-V, --version`: Show version and exit

## Output Formats

The `fields`, `files`, and `search` commands support different output formats:

- **Table** (default): Human-readable formatted output
- `--json`: Pretty-printed JSON (entire result as array/object)
- `--ndjson`: Newline-delimited JSON (one record per line, ideal for LLM consumption)
