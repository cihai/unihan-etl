(quickstart)=

# Quickstart

unihan-etl downloads the Unicode {ref}`UNIHAN <unihan>` database and
exports it to CSV, JSON, or YAML. A plain `unihan-etl export` works out
of the box — the download is cached for reuse.

## Installation

Ensure you have at least Python **>= 3.10**.

Using [uv]:

```console
$ uv add unihan-etl
```

Run the CLI once without a persistent install via [uvx]:

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

unihan-etl publishes alpha, beta, and release-candidate versions to [PyPI](https://pypi.org/project/unihan-etl/).
Their version numbers carry `a1`, `b1`, and `rc1` suffixes, respectively.
For example, `0.27.0a1` is the first alpha release of `0.27.0` before general availability.

- [uv]:

  ```console
  $ uv add unihan-etl --prerelease allow
  ```

- [pip]\:

  ```console
  $ pip install --user --upgrade --pre unihan-etl
  ```

- [pipx]\:

  ```console
  $ pipx install --suffix=@next 'unihan-etl' --pip-args '\--pre' --force
  ```

  Then run `unihan-etl@next export`.

- [uv tool install][uv-tools]:

  ```console
  $ uv tool install --prerelease allow unihan-etl
  ```

- [uvx][uvx]:

  ```console
  $ uvx --from 'unihan-etl' --prerelease allow unihan-etl
  ```

  Then rerun with your desired arguments, e.g. `uvx --prerelease allow unihan-etl export`.

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
[uv-tools]: https://docs.astral.sh/uv/concepts/tools/
[uvx]: https://docs.astral.sh/uv/guides/tools/

## Commands

Run `unihan-etl` without arguments to list its subcommands; the {ref}`CLI reference <cli>` documents each one.

```console
$ unihan-etl
```

## Pythonics

For the rarer cases, you can drive the same pipeline from Python — see the {ref}`API reference <api>` for {class}`~unihan_etl.core.Packager` and {class}`~unihan_etl.options.Options`.
