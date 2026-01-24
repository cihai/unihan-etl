(cli-export)=

# unihan-etl export

Export UNIHAN data to CSV, JSON, or YAML format.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: export
```

## Examples

Export all UNIHAN data to JSON:

```console
$ unihan-etl export -F json
```

Export specific fields:

```console
$ unihan-etl export -F json -f kDefinition kMandarin
```
