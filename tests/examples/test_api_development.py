#!/usr/bin/env python
"""Example of using unihan-etl for API development."""

from __future__ import annotations

from typing import Any, cast

from unihan_etl.core import Packager


class UnihanAPI:
    """Simple API wrapper for UNIHAN data."""

    def __init__(self, data: list[dict[str, Any]]) -> None:
        """Initialize the API with UNIHAN data."""
        self.data = data
        self.characters = {item["char"]: item for item in data}

    def lookup_character(self, char: str) -> dict[str, Any]:
        """Look up a character by its unicode character."""
        return self.characters.get(char, {})

    def search_definition(self, term: str) -> list[dict[str, Any]]:
        """Search for characters by definition."""
        results = []
        for item in self.data:
            definition = item.get("kDefinition", "")
            # Convert definition to string if it's a list
            if isinstance(definition, list):
                definition = " ".join(definition)
            if term.lower() in definition.lower():
                results.append(item)
        return results


def test_api_development(unihan_quick_packager: Packager) -> None:
    """Test developing an API with unihan-etl data."""
    # Download the data
    unihan_quick_packager.download()

    # Set format to python for data export
    unihan_quick_packager.options.format = "python"

    # Get the data
    data = unihan_quick_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Create our API wrapper
    api = UnihanAPI(cast(list[dict[str, Any]], data))

    # Test character lookup
    if data:
        first_char = cast(dict[str, Any], data[0])["char"]
        lookup_result = api.lookup_character(first_char)
        assert lookup_result is not None
        assert "char" in lookup_result
        assert lookup_result["char"] == first_char
