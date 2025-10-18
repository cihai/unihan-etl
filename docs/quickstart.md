(quickstart)=

# Quickstart

## Installation

Assure you have at least python **>= 3.7**.

Using [uv]:

```console
$ uv add unihan-etl
```

Run the CLI once without a persistent install via `uvx`:

```console
$ uvx unihan-etl
```

Using [pip]:

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
For example, `0.27.0a1` is the first alpha release of `0.27.0` before general availability.

- [uv]:

  ```console
  $ uv add --prerelease=allow unihan-etl
  ```

  ```console
  $ uv add --prerelease=allow 'unihan-etl==0.27.0a1'
  ```

  The second command demonstrates pinning to a specific pre-release version.

- [pip]\:

  ```console
  $ pip install --user --upgrade --pre unihan-etl
  ```

- [pipx]\:

  ```console
  $ pipx install --suffix=@next 'unihan-etl' --pip-args '\--pre' --force
  ```

  Then run `unihan-etl@next load [session]`.

- `uvx`:

  ```console
  $ uvx --prerelease=allow unihan-etl
  ```

  ```console
  $ uvx --from 'unihan-etl==0.27.0a1' unihan-etl
  ```

  The second command runs the pinned pre-release without installing it.

  Then rerun with your desired arguments, e.g. `uvx --prerelease=allow unihan-etl load [session]`.

via trunk (can break easily):

- [pip]\:

  ```console
  $ pip install --user -e git+https://github.com/cihai/unihan-etl.git#egg=unihan-etl
  ```

- [pipx]\:

  ```console
  $ pipx install --suffix=@master 'unihan-etl @ git+https://github.com/cihai/unihan-etl.git@master' --force
  ```

- `uvx`\*:

  ```console
  $ uvx --from git+https://github.com/cihai/unihan-etl.git@master unihan-etl
  ```

  \*`uvx --from` lets you run directly from a VCS URL.

[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pypa.github.io/pipx/docs/
[uv]: https://docs.astral.sh/uv/

## Commands

```console
$ unihan-etl
```

## Pythonics

:::{seealso}

{ref}`unihan-etl API documentation <api>`.
