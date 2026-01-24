(cli-download)=

# unihan-etl download

Download and cache the UNIHAN database without exporting.

## Command

```{eval-rst}
.. argparse::
    :module: unihan_etl.cli
    :func: create_parser
    :prog: unihan-etl
    :path: download
```

## Examples

Download and cache without exporting:

```console
$ unihan-etl download
```

Force re-download:

```console
$ unihan-etl download --no-cache
```
