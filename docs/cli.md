(cli)=

# Commands

unihan-etl provides a subcommand-based CLI for working with UNIHAN data.

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

## Global Options

- `--color {auto,always,never}`: Color output mode (default: auto)
- `-l, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: Logging level (default: INFO)
- `-V, --version`: Show version and exit

## Output Formats

The `fields`, `files`, and `search` commands support different output formats:

- **Table** (default): Human-readable formatted output
- `--json`: Pretty-printed JSON (entire result as array/object)
- `--ndjson`: Newline-delimited JSON (one record per line, ideal for LLM consumption)

## Command Reference

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
```

## Examples

### Export Data

Export all UNIHAN data to JSON:

```console
$ unihan-etl export -F json
```

Export specific fields:

```console
$ unihan-etl export -F json -f kDefinition kMandarin
```

### Download Only

Download and cache without exporting:

```console
$ unihan-etl download
```

Force re-download:

```console
$ unihan-etl download --no-cache
```

### List Fields

List all available fields:

```console
$ unihan-etl fields
```

List fields as JSON (for programmatic use):

```console
$ unihan-etl fields --json
```

List fields from a specific file:

```console
$ unihan-etl fields -i Unihan_Readings.txt
```

### List Files

List available UNIHAN source files:

```console
$ unihan-etl files
```

Include field names for each file:

```console
$ unihan-etl files --with-fields --json
```

### Search Characters

Look up a character by its form:

```console
$ unihan-etl search 一
```

Look up by UCN:

```console
$ unihan-etl search U+4E00
```

Look up by hex codepoint:

```console
$ unihan-etl search 4E00
```

Get JSON output for LLM consumption:

```console
$ unihan-etl search 一 --json
```

Filter to specific fields:

```console
$ unihan-etl search 一 -f kDefinition kMandarin
```
