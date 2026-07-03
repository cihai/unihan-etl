(cli-export)=

# unihan-etl export

Export {ref}`UNIHAN <unihan>` data to CSV, JSON, or YAML format.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: export
```

## Examples

Export with the defaults — CSV, with the download cached:

```console
$ unihan-etl export
```

Export all UNIHAN data to JSON:

```console
$ unihan-etl export -F json
```

Export specific fields:

```console
$ unihan-etl export -F json -f kDefinition kMandarin
```
