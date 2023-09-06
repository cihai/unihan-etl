(quickstart)=

# Quickstart

## Installation

Assure you have at least python **>= 3.7**.

```console
$ pip install --user unihan-etl
```

You can upgrade to the latest release with:

```console
$ pip install --user --upgrade unihan-etl
```

(developmental-releases)=

### Developmental releases

New versions of unihan-etl are published to PyPI as alpha, beta, or release candidates.
In their versions you will see notification like `a1`, `b1`, and `rc1`, respectively.
`1.10.0b4` would mean the 4th beta release of `1.10.0` before general availability.

- [pip]\:

  ```console
  $ pip install --user --upgrade --pre unihan-etl
  ```

- [pipx]\:

  ```console
  $ pipx install --suffix=@next 'unihan-etl' --pip-args '\--pre' --force
  ```

  Then use `unihan-etl@next load [session]`.

via trunk (can break easily):

- [pip]\:

  ```console
  $ pip install --user -e git+https://github.com/cihai/unihan-etl.git#egg=unihan-etl
  ```

- [pipx]\:

  ```console
  $ pipx install --suffix=@master 'unihan-etl @ git+https://github.com/cihai/unihan-etl.git@master' --force
  ```

[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pypa.github.io/pipx/docs/

## Commands

```console
$ unihan-etl
```

## Pythonics

:::{seealso}

{ref}`unihan-etl API documentation <api>`.
