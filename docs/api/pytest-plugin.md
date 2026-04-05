(pytest_plugin)=

# `pytest` plugin

:::{doc-pytest-plugin} unihan_etl.pytest_plugin
:project: unihan-etl
:package: unihan-etl
:summary: unihan-etl ships a pytest plugin that downloads UNIHAN.zip once and reuses it across tests.
:tests-url: https://github.com/cihai/unihan-etl/tree/master/tests

Use these fixtures when your test suite needs a repeatable UNIHAN dataset plus
an isolated home directory for cache and config setup.

## Recommended fixtures

The plugin stays intentionally explicit. These fixtures are the common setup:

- {fixture}`set_home` patches `$HOME` to point at {fixture}`user_path`.
- {fixture}`home_path` and {fixture}`user_path` create disposable filesystem
  roots for each test run.
- The dataset fixtures keep `UNIHAN.zip` cached so tests can reuse it without
  re-downloading the archive every time.

## Bootstrapping in `conftest.py`

Make the environment setup explicit in your own suite:

```python
import pytest


@pytest.fixture(autouse=True)
def setup(
    set_home: None,
) -> None:
    pass
```
:::
