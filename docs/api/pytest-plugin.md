(pytest_plugin)=

# `pytest` plugin

unihan-etl ships a pytest plugin that downloads `UNIHAN.zip` once and reuses
it across tests, plus an isolated home directory for cache and config setup.
The plugin auto-discovers via the `pytest11` entry point — installing
`unihan-etl` is enough to make every fixture below available in your tests.
See the [test suite](https://github.com/cihai/unihan-etl/tree/master/tests)
for usage examples.

## Quick Start

Add a fixture name as a test parameter — pytest creates and injects it automatically. You never call fixtures yourself.

```python
def test_quick_packager(unihan_quick_packager) -> None:
    unihan_quick_packager.download()
    unihan_quick_packager.export()
    assert unihan_quick_packager.options.destination.exists()


def test_with_raw_snippet(unihan_quick_data: str) -> None:
    assert "kCantonese" in unihan_quick_data
```

## Which Fixture Do I Need?

- Use {fixture}`unihan_quick_packager` when you want a small, fast UNIHAN dataset for unit tests.
- Use {fixture}`unihan_full_packager` when you need the complete UNIHAN corpus.
- Use {fixture}`unihan_bootstrap_all` (autouse-wrapped) when you want both datasets pre-downloaded at session start.
- Use {fixture}`unihan_quick_data` when you only need a raw text snippet rather than a fully bootstrapped Packager.
- Override {fixture}`unihan_cache_path` (or {fixture}`unihan_project_cache_path`) to redirect where cached UNIHAN data lives.
- Override {fixture}`unihan_home_user_name` when you need a custom test user identity.

---

## Dataset Bootstrap

The primary injection points for tests that need a working UNIHAN dataset.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_packager

   .. rubric:: Example

   .. code-block:: python

      def test_quick(unihan_quick_packager) -> None:
          unihan_quick_packager.download()
          unihan_quick_packager.export()
          assert unihan_quick_packager.options.destination.exists()

.. autofixture:: unihan_etl.pytest_plugin.unihan_full_packager

.. autofixture:: unihan_etl.pytest_plugin.unihan_ensure_quick

.. autofixture:: unihan_etl.pytest_plugin.unihan_ensure_full

.. autofixture:: unihan_etl.pytest_plugin.unihan_bootstrap_all

   .. rubric:: Example

   .. code-block:: python

      # conftest.py
      import pytest


      @pytest.fixture(scope="session", autouse=True)
      def bootstrap(unihan_bootstrap_all) -> None:
          return None
```

## Dataset Options & Paths

Session-scoped fixtures exposing the dataset filesystem layout and the
{class}`~unihan_etl.options.Options` objects that drive the {class}`~unihan_etl.core.Packager`.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_options

.. autofixture:: unihan_etl.pytest_plugin.unihan_full_options

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_full_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_zip_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_zip
```

## Raw Data Accessors

Lower-level fixtures for tests that need to inspect or transform UNIHAN data
without invoking the full Packager pipeline.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_data

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_fixture_files

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_columns

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_normalized_data

.. autofixture:: unihan_etl.pytest_plugin.unihan_quick_expanded_data
```

## Mock Zip Fixtures

Build a synthetic `Unihan.zip` on disk for tests that exercise the download/extract
path without hitting the real corpus.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_mock_zip

.. autofixture:: unihan_etl.pytest_plugin.unihan_mock_zip_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_mock_zip_pathname

.. autofixture:: unihan_etl.pytest_plugin.unihan_mock_test_dir
```

## Cache Paths (Override Hooks)

Override these in your project's `conftest.py` to redirect where unihan-etl caches
downloaded archives, extracted files, and intermediate fixture state.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_user_cache_path
   :kind: override_hook

.. autofixture:: unihan_etl.pytest_plugin.unihan_project_cache_path
   :kind: override_hook

.. autofixture:: unihan_etl.pytest_plugin.unihan_cache_path
   :kind: override_hook

   .. rubric:: Example

   .. code-block:: python

      # conftest.py
      import pathlib
      import pytest


      @pytest.fixture(scope="session")
      def unihan_cache_path(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
          return tmp_path_factory.mktemp("unihan-cache")

.. autofixture:: unihan_etl.pytest_plugin.unihan_fixture_root
   :kind: override_hook
```

## Home & User Environment

Create an isolated filesystem home for the duration of the test session. Override
{fixture}`unihan_home_user_name` to control the user identity.

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_home_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_home_user_name
   :kind: override_hook

   .. rubric:: Example

   .. code-block:: python

      # conftest.py
      import pytest


      @pytest.fixture(scope="session")
      def unihan_home_user_name() -> str:
          return "ci-runner"

.. autofixture:: unihan_etl.pytest_plugin.unihan_user_path

.. autofixture:: unihan_etl.pytest_plugin.unihan_zshrc
```

## Function-Scoped Helpers

```{eval-rst}
.. autofixture:: unihan_etl.pytest_plugin.unihan_test_options
```

---

## Types

```{eval-rst}
.. autodata:: unihan_etl.pytest_plugin.UnihanTestOptions
```

---

## Configuration

These `conf.py` values control how fixture documentation is rendered:

```{eval-rst}
.. confval:: pytest_fixture_hidden_dependencies

   Fixture names to suppress from "Depends on" lists. Default: common pytest
   builtins (:external+pytest:std:fixture:`pytestconfig`,
   :external+pytest:std:fixture:`capfd`,
   :external+pytest:std:fixture:`capsysbinary`,
   :external+pytest:std:fixture:`capfdbinary`,
   :external+pytest:std:fixture:`recwarn`,
   :external+pytest:std:fixture:`tmpdir`,
   :external+pytest:std:fixture:`pytester`,
   :external+pytest:std:fixture:`testdir`,
   :external+pytest:std:fixture:`record_property`,
   ``record_xml_attribute``,
   :external+pytest:std:fixture:`record_testsuite_property`,
   :external+pytest:std:fixture:`cache`).

.. confval:: pytest_fixture_builtin_links

   URL mapping for builtin fixture external links in "Depends on" blocks.
   Default: links to pytest docs for
   :external+pytest:std:fixture:`tmp_path_factory`,
   :external+pytest:std:fixture:`tmp_path`,
   :external+pytest:std:fixture:`monkeypatch`,
   :external+pytest:std:fixture:`request`,
   :external+pytest:std:fixture:`capsys`,
   :external+pytest:std:fixture:`caplog`.

.. confval:: pytest_external_fixture_links

   URL mapping for external fixture cross-references. Default: ``{}``.
```

---

```{note}
All fixtures above are also auto-discoverable via:

    .. autofixtures:: unihan_etl.pytest_plugin
       :order: source

Use ``autofixtures::`` in your own plugin docs to document every fixture from a
module without listing each one manually.
```
