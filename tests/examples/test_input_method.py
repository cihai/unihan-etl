#!/usr/bin/env python
"""Example of using unihan-etl for input method development."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_input_method_development(unihan_quick_packager: Packager) -> None:
    """Test input method development with UNIHAN data."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python to get data back
    unihan_quick_packager.options.format = "python"

    # Create a packager focused on pronunciation data
    options = {
        "fields": ["kDefinition", "kMandarin"],
    }

    # Create the packager
    pinyin_packager = Packager(options)

    # Download the data
    pinyin_packager.download()

    # Set format to python for data export
    pinyin_packager.options.format = "python"

    # Get the data
    data = pinyin_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Create a simple pinyin-to-character mapping
    pinyin_to_chars: dict[str, list[str]] = {}

    # Build a simple input method dictionary
    for item in data:
        # Get the pinyin (Mandarin pronunciation)
        pinyin = item.get("kMandarin", "")

        # Handle different data types
        if isinstance(pinyin, list):
            pinyin = pinyin[0] if pinyin else ""
        elif isinstance(pinyin, dict):
            pinyin = str(pinyin)

        # Skip if no pinyin
        if not pinyin:
            continue

        # Make sure pinyin is a string key
        pinyin_key = str(pinyin)

        # Add to our input method dictionary
        if pinyin_key not in pinyin_to_chars:
            pinyin_to_chars[pinyin_key] = []

        pinyin_to_chars[pinyin_key].append(item["char"])

    # Verify our input method dictionary has entries
    assert len(pinyin_to_chars) > 0

    # Example function for using our input method
    def lookup_by_pinyin(pinyin: str) -> list[str]:
        """Look up characters by pinyin pronunciation."""
        return pinyin_to_chars.get(pinyin, [])
