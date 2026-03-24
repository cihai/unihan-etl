(api)=

(reference)=

# API Reference

```{module} unihan_etl

```

:::{warning}
APIs are **not** considered stable before 1.0. They can break or be removed between minor versions.

If you need an API stabilized please [file an issue](https://github.com/cihai/unihan-etl/issues).
:::

## Core Modules

::::{grid} 1 2 3 3
:gutter: 2 2 3 3

:::{grid-item-card} Core
:link: core
:link-type: doc
ETL pipeline and Packager: download, normalize, export.
:::

:::{grid-item-card} Options
:link: options
:link-type: doc
Configuration dataclass for paths, formats, and field selection.
:::

:::{grid-item-card} Expansion
:link: expansion
:link-type: doc
Expand multi-value UNIHAN fields into structured data.
:::

:::{grid-item-card} Types
:link: types
:link-type: doc
Shared TypedDicts and type aliases.
:::

:::{grid-item-card} Constants
:link: constants
:link-type: doc
Field lists, manifests, and default paths.
:::

:::{grid-item-card} Utils
:link: utils
:link-type: doc
Helpers for progress, codepoints, and field resolution.
:::

::::

## Test Utilities

::::{grid} 1 1 2 2
:gutter: 2 2 3 3

:::{grid-item-card} Test
:link: test
:link-type: doc
Legacy test harness.
:::

:::{grid-item-card} pytest plugin
:link: pytest-plugin
:link-type: doc
Fixtures for quick and full UNIHAN datasets in pytest.
:::

::::

```{toctree}
:hidden:

core
options
expansion
types
constants
utils
test
pytest-plugin
```
