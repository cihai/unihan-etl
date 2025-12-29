(pytest_plugin)=

# `pytest` plugin

Download and reuse UNIHAN data on the fly in [pytest].

```{module} unihan_etl.pytest_plugin

```

[pytest]: https://docs.pytest.org/

## Usage

Install `unihan-etl` via the package manager of your choosing:

```console
$ uv add unihan-etl
```

The pytest plugin is automatically detected via pytest, and fixtures are available.

## Quick Start

The plugin provides two dataset tiers:

- **quick**: Bundled subset (~140KB), no network required - use for unit tests
- **full**: Complete UNIHAN dataset (~20MB), downloads once - use for integration tests

### Basic Usage

```python
from unihan_etl.types import UnihanDataset, UnihanZip

def test_quick_dataset(unihan_quick: UnihanDataset) -> None:
    """Test with the quick (bundled) dataset."""
    assert unihan_quick.name == "quick"
    assert unihan_quick.zip.exists()

    # Access zip contents
    with unihan_quick.zip.open() as zf:
        assert "Unihan_Readings.txt" in zf.namelist()
```

### With Extracted Data

```python
def test_with_data(
    unihan_quick: UnihanDataset,
    unihan_ensure_quick: None,  # Ensures data is extracted
) -> None:
    """Test with extracted data."""
    assert unihan_quick.is_ready
    assert unihan_quick.destination.exists()
```

### Lazy Data Loading

```python
from unihan_etl.types import UnihanData

def test_lazy_data(unihan_quick_data_lazy: UnihanData) -> None:
    """Data only loads when accessed."""
    # Not loaded yet...
    expanded = unihan_quick_data_lazy.expanded  # Loads on access
    by_char = unihan_quick_data_lazy.by_char    # Cached after first load

    assert "丘" in by_char or len(expanded) > 0
```

## Dataset Types

### UnihanZip

Container for UNIHAN zip file with lazy access:

```python
import pathlib

from unihan_etl.types import UnihanZip

def test_zip(unihan_quick_zip: UnihanZip, tmp_path: pathlib.Path) -> None:
    # Path access
    assert unihan_quick_zip.path.exists()
    assert unihan_quick_zip.exists()

    # Context manager for open handle
    with unihan_quick_zip.open() as zf:
        files = zf.namelist()

    # Convenience property
    files = unihan_quick_zip.namelist

    # Extract to destination
    unihan_quick_zip.extract(tmp_path)
```

### UnihanDataset

Complete dataset container with all paths:

```python
from unihan_etl.types import UnihanDataset

def test_dataset(unihan_quick: UnihanDataset) -> None:
    assert unihan_quick.name in ("quick", "full")
    assert isinstance(unihan_quick.zip, UnihanZip)
    assert isinstance(unihan_quick.work_dir, pathlib.Path)
    assert isinstance(unihan_quick.destination, pathlib.Path)
    assert isinstance(unihan_quick.is_ready, bool)
```

### UnihanData

Lazy-loaded data container:

```python
from unihan_etl.types import UnihanData

def test_data(unihan_quick_data_lazy: UnihanData) -> None:
    # Properties load data on first access
    normalized = unihan_quick_data_lazy.normalized  # Raw normalized data
    expanded = unihan_quick_data_lazy.expanded      # Expanded delimited fields
    by_char = unihan_quick_data_lazy.by_char        # Dict keyed by character
```

## CLI Options

### `--unihan-cache-dir`

Override the cache directory:

```console
$ pytest --unihan-cache-dir=/tmp/my-cache
```

## Markers

### `@pytest.mark.unihan_full`

Mark tests that require the full UNIHAN dataset:

```python
import pytest
from unihan_etl.types import UnihanDataset

@pytest.mark.unihan_full
def test_full_dataset(
    unihan_full: UnihanDataset,
    unihan_ensure_full: None,
) -> None:
    """This test requires the full dataset (~26MB download)."""
    assert unihan_full.is_ready
```

## Fixture Reference

### Primary Fixtures

| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `unihan_quick` | session | `UnihanDataset` | Quick dataset container |
| `unihan_full` | session | `UnihanDataset` | Full dataset container |
| `unihan_quick_zip` | session | `UnihanZip` | Quick dataset zip container |
| `unihan_ensure_quick` | session | `None` | Extracts quick dataset |
| `unihan_ensure_full` | session | `None` | Downloads and extracts full dataset |
| `unihan_quick_data_lazy` | session | `UnihanData` | Lazy-loaded quick data |

### Path Fixtures

| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `unihan_cache_path` | session | `Path` | Cache directory (overridable) |
| `unihan_fixture_root` | session | `Path` | Root for fixture data |
| `unihan_quick_path` | session | `Path` | Quick dataset directory |
| `unihan_full_path` | session | `Path` | Full dataset directory |

### Options/Packager Fixtures

| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `unihan_quick_options` | session | `UnihanOptions` | Options for quick dataset |
| `unihan_full_options` | session | `UnihanOptions` | Options for full dataset |
| `unihan_quick_packager` | session | `Packager` | Packager for quick dataset |
| `unihan_full_packager` | session | `Packager` | Packager for full dataset |

### Data Fixtures

| Fixture | Scope | Returns | Description |
|---------|-------|---------|-------------|
| `unihan_quick_normalized_data` | session | `UntypedNormalizedData` | Normalized quick data |
| `unihan_quick_expanded_data` | session | `ExpandedExport` | Expanded quick data |
| `unihan_quick_data` | session | `str` | Raw UNIHAN excerpt |

## Overriding Fixtures

Override `unihan_cache_path` to customize cache location:

```python
# conftest.py
import pathlib
import pytest

@pytest.fixture(scope="session")
def unihan_cache_path() -> pathlib.Path:
    """Use a custom cache location."""
    return pathlib.Path("/my/custom/cache")
```

## See Also

- [unihan-etl tests](https://github.com/cihai/unihan-etl/tree/master/tests) - Example usage
- [MIGRATION](https://github.com/cihai/unihan-etl/blob/master/MIGRATION) - Breaking changes

## API Reference

```{eval-rst}
.. automodule:: unihan_etl.pytest_plugin
    :members:
    :inherited-members:
    :private-members:
    :show-inheritance:
    :member-order: bysource
```
