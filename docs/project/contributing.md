(contributing)=

# Contributing

unihan-etl is part of the [cihai project](https://cihai.git-pull.com/). Development
conventions, issue triage, and PR guidelines follow the shared cihai contributing
guide:

> <https://cihai.git-pull.com/contributing/>

## Quick start

Clone the repository:

```console
$ git clone https://github.com/cihai/unihan-etl.git
```

Enter the project directory:

```console
$ cd unihan-etl
```

Install the development dependencies:

```console
$ uv sync --group dev
```

Run the test suite:

```console
$ uv run py.test
```

## Continuous testing

Re-run the tests on every change with [pytest-watcher](https://github.com/olzhasar/pytest-watcher):

```console
$ uv run ptw .
```
