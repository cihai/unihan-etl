#!/usr/bin/env python
"""Example of basic unihan-etl usage."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_basic_process(unihan_quick_packager: Packager) -> None:
    """Test basic usage of the Packager class to get data."""
    # First download the data
    unihan_quick_packager.download()

    # Update options to use python format to get data back
    unihan_quick_packager.options.format = "python"

    # Use export() to get data
    data = unihan_quick_packager.export()

    # Verify we got data
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify structure of the data
    for item in data[:5]:  # Check first 5 items
        # Each item should have a character and unicode code point
        assert "char" in item
        assert "ucn" in item

        # Verify the character is a string
        assert isinstance(item["char"], str)

        # Verify the UCN has the right format
        assert item["ucn"].startswith("U+")
