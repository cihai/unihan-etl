#!/usr/bin/env python
"""Example of filtering characters in unihan-etl."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_character_filtering(unihan_quick_packager: Packager) -> None:
    """Test filtering characters in the UNIHAN dataset."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python to get data back
    unihan_quick_packager.options.format = "python"

    # Get all characters first to find some valid ones
    all_data = unihan_quick_packager.export()

    # Make sure we have data
    assert all_data is not None
    assert len(all_data) > 0

    # Get the first few characters to filter
    if all_data:
        # Create options with field filter only, no character filter
        options = {
            "fields": ["kDefinition", "kMandarin"],
        }

        # Create a new packager with character filter
        filtered_packager = Packager(options)

        # Download the filtered data
        filtered_packager.download()

        # Set format to python to get data back
        filtered_packager.options.format = "python"

        # Get the filtered data
        filtered_data = filtered_packager.export()

        # Verify we got data
        assert filtered_data is not None

        # Get a couple specific characters from the data
        specific_chars = [item["char"] for item in filtered_data[:3]]

        # Filter just those specific characters
        char_data = [item for item in filtered_data if item["char"] in specific_chars]

        # Verify we have data for our specific characters
        assert len(char_data) > 0
        assert all(item["char"] in specific_chars for item in char_data)
