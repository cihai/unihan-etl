(cli)=

# Commands

unihan-etl provides a subcommand-based CLI for working with UNIHAN data.

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

## Usage

Running `unihan-etl` without arguments shows help with available commands:

```console
$ unihan-etl
```

## Available Commands

| Command | Description |
|---------|-------------|
| `export` | Export UNIHAN data to CSV, JSON, or YAML |
| `download` | Download and cache UNIHAN database |
| `fields` | List available UNIHAN fields |
| `files` | List available UNIHAN source files |
| `search` | Look up character data |

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

- `--color {auto,always,never}`: Color output mode (default: auto)
- `-l, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Logging level (default: INFO)
- `-V, --version`: Show version and exit

## Output Formats

The `fields`, `files`, and `search` commands support different output formats:

- **Table** (default): Human-readable formatted output
- `--json`: Pretty-printed JSON (entire result as array/object)
- `--ndjson`: Newline-delimited JSON (one record per line, ideal for LLM consumption)
