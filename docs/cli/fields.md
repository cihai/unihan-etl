(cli-fields)=

# unihan-etl fields

List available UNIHAN fields with their descriptions and source files.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: fields
```

## Examples

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
