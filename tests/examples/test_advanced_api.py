#!/usr/bin/env python
"""Example of building advanced processing with unihan-etl."""

from __future__ import annotations

from typing import Any, cast

from unihan_etl.core import Packager


def test_custom_processing_pipeline(unihan_quick_packager: Packager) -> None:
    """Test custom data processing with UNIHAN data."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python for data export
    unihan_quick_packager.options.format = "python"

    # For this test, we are designing a custom pipeline
    # that applies a series of transformations to the data
    # to create a specialized dataset

    # Get the data
    data = unihan_quick_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Processing step 1: Extract only the fields we need
    def extract_fields(item: dict[str, Any]) -> dict[str, Any]:
        """Extract only the fields we need for our processing."""
        return {
            "char": item["char"],
            "ucn": item["ucn"],
            "definition": item.get("kDefinition", ""),
            "mandarin": item.get("kMandarin", ""),
        }

    # Processing step 2: Filter to only include items with definitions
    def has_definition(item: dict[str, Any]) -> bool:
        """Check if an item has a definition."""
        return bool(item.get("definition"))

    # Apply our custom pipeline
    result = (
        # First extract the fields we need
        [extract_fields(cast(dict[str, Any], item)) for item in data]
        # Then filter to only include items with definitions
        if data
        else []
    )
    filtered_result = [item for item in result if has_definition(item)]

    # Verify our pipeline worked
    if filtered_result:
        # If we have results, check they all have definitions
        for item in filtered_result:
            assert "definition" in item
            assert item["definition"]
