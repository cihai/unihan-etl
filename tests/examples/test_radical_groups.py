#!/usr/bin/env python
"""Example of grouping characters by radical using UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_radical_grouping(unihan_quick_packager: Packager) -> None:
    """Demonstrate grouping characters by radical."""
    # Set options for radical and stroke fields
    options = {
        "fields": ["kRSUnicode", "kTotalStrokes", "kDefinition"],
    }

    # Create a packager with the fields we need
    radical_packager = Packager(options)

    # Download the data
    radical_packager.download()

    # Set format to python to get data back
    radical_packager.options.format = "python"

    # Get the data
    data = radical_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Helper function to extract radical from kRSUnicode
    def extract_radical(rs_unicode: Any) -> int | None:
        """Extract radical number from kRSUnicode field."""
        if not rs_unicode:
            return None

        # Handle different data types
        if isinstance(rs_unicode, list):
            # Take the first one if it's a list
            if not rs_unicode:
                return None
            first_value = rs_unicode[0]

            # Handle potentially complex structures
            if isinstance(first_value, str) and "." in first_value:
                parts = first_value.split(".")
                try:
                    return int(parts[0])
                except (ValueError, TypeError):
                    return None
            try:
                return int(first_value)
            except (ValueError, TypeError):
                return None
        elif isinstance(rs_unicode, str) and "." in rs_unicode:
            parts = rs_unicode.split(".")
            try:
                return int(parts[0])
            except (ValueError, TypeError):
                return None

        return None

    # Group characters by radical
    def group_by_radical(
        char_data: list[dict[str, Any]],
    ) -> dict[int, list[dict[str, Any]]]:
        """Group characters by their radical number."""
        groups: dict[int, list[dict[str, Any]]] = {}

        for item in char_data:
            rs_unicode = item.get("kRSUnicode")
            if not rs_unicode:
                continue

            radical = extract_radical(rs_unicode)
            if radical is not None:
                if radical not in groups:
                    groups[radical] = []
                groups[radical].append(item)

        return groups

    # Convert data to list of dictionaries for easier processing
    char_data_list = []
    if data is not None:
        char_data_list = [dict(item) for item in data]

    # Create radical groups
    radical_groups = group_by_radical(char_data_list)

    # Print some diagnostic info
    print(f"Found {len(data)} total characters")
    print(f"Found {len(radical_groups)} radical groups")

    # Test with different radicals if we have data
    if radical_groups:
        # Look at a few radical groups
        for radical in sorted(radical_groups.keys())[:5]:
            chars = radical_groups[radical]
            print(f"Radical {radical}: {len(chars)} characters")

        # Take a sample group
        sample_radical = next(iter(radical_groups.keys()))
        chars_in_group = radical_groups[sample_radical]

        # Check that all chars in the group have the same radical
        for char in chars_in_group:
            extracted = extract_radical(char.get("kRSUnicode"))
            assert extracted == sample_radical
