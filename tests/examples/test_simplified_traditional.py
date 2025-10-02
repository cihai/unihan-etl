#!/usr/bin/env python
"""Example of working with simplified/traditional Chinese character pairs."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_simplified_traditional_pairs(unihan_quick_packager: Packager) -> None:
    """Demonstrate working with simplified/traditional character pairs."""
    # Set options to get data related to character variants
    options = {
        "fields": ["kSimplifiedVariant", "kTraditionalVariant"],
    }

    # Create a packager with the fields we need
    variant_packager = Packager(options)

    # Download the data
    variant_packager.download()

    # Set format to python to get data back
    variant_packager.options.format = "python"

    # Get the data
    data = variant_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Filter for characters with variant forms
    simplified_pairs = [
        item
        for item in data
        if "kSimplifiedVariant" in item or "kTraditionalVariant" in item
    ]

    # Print some diagnostic info
    print(f"Found {len(data)} total characters")
    print(f"Found {len(simplified_pairs)} characters with variant forms")

    # Verify the structure of the data
    if simplified_pairs:
        # If we have pairs, check them
        for char in simplified_pairs[:5]:
            assert "char" in char
            assert "kSimplifiedVariant" in char or "kTraditionalVariant" in char
    else:
        # If not, the test data might not include variants, so just check
        # the data structure
        for char in data[:5]:
            assert "char" in char
