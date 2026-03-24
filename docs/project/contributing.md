(contributing)=

# Contributing

unihan-etl is part of the [cihai project](https://cihai.git-pull.com/). Development
conventions, issue triage, and PR guidelines follow the shared cihai contributing
guide:

> <https://cihai.git-pull.com/contributing/>

## Quick start

```console
$ git clone https://github.com/cihai/unihan-etl.git
```

```console
$ cd unihan-etl
```

```console
$ uv sync --group dev
```

```console
$ uv run py.test
```

## Continuous testing

```console
$ uv run ptw .
```
