(cli-files)=

# unihan-etl files

List available UNIHAN source files.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: files
```

## Examples

List available UNIHAN source files:

```console
$ unihan-etl files
```

Include field names for each file:

```console
$ unihan-etl files --with-fields --json
```
