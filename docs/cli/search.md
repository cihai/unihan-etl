(cli-search)=

# unihan-etl search

Look up character data in the {ref}`UNIHAN <unihan>` database.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: search
```

## Examples

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

Get the result as JSON:

```console
$ unihan-etl search 一 --json
```

Filter to specific fields:

```console
$ unihan-etl search 一 -f kDefinition kMandarin
```
