#!/usr/bin/env python
"""Example of looking up UNIHAN character data."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_character_lookup(unihan_quick_packager: Packager) -> None:
    """Test retrieving specific character information."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python to get data back
    unihan_quick_packager.options.format = "python"

    # Get data for a specific character (e.g. 一)
    result = unihan_quick_packager.export()

    # Verify we got some data
    assert result is not None
    assert len(result) > 0
