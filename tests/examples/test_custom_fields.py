#!/usr/bin/env python
"""Example of using custom fields with unihan-etl."""

from __future__ import annotations

from typing import Any, cast

from unihan_etl.core import Packager


def test_custom_fields(unihan_quick_packager: Packager) -> None:
    """Test using custom fields with UNIHAN data."""
    # Download the data
    unihan_quick_packager.download()

    # Set format to python for data export
    unihan_quick_packager.options.format = "python"

    # Get the data
    data = unihan_quick_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Process a subset of the data
    subset = (
        cast(list[dict[str, Any]], data)[:5]
        if len(data) > 5
        else cast(list[dict[str, Any]], data)
    )

    # Create a custom function to add our own fields
    # (In a real application this could be much more complex)
    def add_custom_fields(item: dict[str, Any]) -> dict[str, Any]:
        """Add custom fields to a UNIHAN data item."""
        # Make a copy to avoid modifying original data
        result = dict(item)

        # Add custom field: simplified flag
        result["custom_simplified"] = False
        if "kSimplifiedVariant" in result:
            result["custom_simplified"] = True

        # Add custom field: has_definition
        result["custom_has_definition"] = "kDefinition" in result

        return result

    # Apply our function to add custom fields
    processed_data = [add_custom_fields(item) for item in subset]

    # Verify our custom fields are present
    for item in processed_data:
        assert "custom_simplified" in item
        assert "custom_has_definition" in item
        assert isinstance(item["custom_simplified"], bool)
        assert isinstance(item["custom_has_definition"], bool)
