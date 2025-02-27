(basic-usage)=

# Basic Usage

This section demonstrates the fundamental ways to use UNIHAN-ETL to access Chinese character data.

## Getting Started

The most basic way to use UNIHAN-ETL is through the `Packager` class, which handles downloading, processing, and exporting UNIHAN data:

```{literalinclude} ../../tests/examples/test_basic_usage.py
:language: python
:linenos:
:caption: Basic UNIHAN-ETL usage
```

## Character Lookup

UNIHAN-ETL makes it easy to look up information about specific characters:

```{literalinclude} ../../tests/examples/test_character_lookup.py
:language: python
:linenos:
:caption: Looking up character information
```

## Working with UNIHAN Fields

UNIHAN-ETL provides access to all fields in the UNIHAN database:

```{literalinclude} ../../tests/examples/test_unihan_fields.py
:language: python
:linenos:
:caption: Working with UNIHAN fields
```

## Key Concepts

When working with UNIHAN-ETL, keep these concepts in mind:

- **Packager**: The main class that handles downloading, processing, and exporting data
- **Options**: Configuration options for the Packager, including which fields to include
- **Fields**: The specific data points about each character (e.g., definitions, pronunciations)
- **Export Formats**: Data can be exported as Python objects, CSV, JSON, or YAML

## Tips for Basic Usage

- Start with simple queries to get familiar with the data structure
- Explore the available fields to understand what data is available
- Use the Python export format for easier data manipulation
- Check data types, as some fields may return strings while others return lists
