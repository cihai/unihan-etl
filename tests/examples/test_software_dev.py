#!/usr/bin/env python
"""Example of using unihan-etl for software development applications."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_dictionary_data_extraction(unihan_quick_packager: Packager) -> None:
    """Test extracting dictionary data from UNIHAN for software development."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python to get data back
    unihan_quick_packager.options.format = "python"

    # Download all data
    data = unihan_quick_packager.export()

    # Verify we got some data
    assert data is not None
    assert len(data) > 0

    # Build a dictionary application data structure
    dictionary_entries: list[dict[str, Any]] = []

    # Process data for a sample of characters (first 100 or all if less)
    sample_data = data[:100] if len(data) > 100 else data

    for item in sample_data:
        # Skip items without the necessary data
        if "char" not in item:
            continue

        # Get the character
        character = item["char"]

        # Extract definitions (could be a string or list)
        definitions = item.get("kDefinition", "")
        if not isinstance(definitions, str):
            if isinstance(definitions, list) and definitions:
                definitions = "; ".join([str(d) for d in definitions])
            else:
                definitions = str(definitions)

        # Extract pronunciations (could be strings or lists)
        mandarin = item.get("kMandarin", "")
        cantonese = item.get("kCantonese", "")

        # Convert to strings if needed
        if not isinstance(mandarin, str):
            if isinstance(mandarin, list) and mandarin:
                mandarin = ", ".join([str(p) for p in mandarin])
            else:
                mandarin = str(mandarin)

        if not isinstance(cantonese, str):
            if isinstance(cantonese, list) and cantonese:
                cantonese = ", ".join([str(p) for p in cantonese])
            else:
                cantonese = str(cantonese)

        # Create dictionary entry
        entry = {
            "character": character,
            "unicode": item.get("ucn", ""),
            "definitions": definitions,
            "pronunciations": {
                "mandarin": mandarin,
                "cantonese": cantonese,
            },
        }

        dictionary_entries.append(entry)

    # Verify we created some dictionary entries
    assert len(dictionary_entries) > 0

    # Verify the structure of our dictionary entries
    for entry in dictionary_entries:
        assert "character" in entry
        assert "definitions" in entry
        assert "pronunciations" in entry
        assert "mandarin" in entry["pronunciations"]
        assert "cantonese" in entry["pronunciations"]
