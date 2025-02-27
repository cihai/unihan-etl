#!/usr/bin/env python
"""Example of performing cross-language comparisons with UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_cross_language_comparison(unihan_quick_packager: Packager) -> None:
    """Demonstrate analyzing characters across different languages."""
    # Set options for multi-language fields
    options = {
        "fields": ["kMandarin", "kJapaneseOn", "kKorean", "kVietnamese", "kCantonese"],
    }

    # Create a packager with the fields we need
    lang_packager = Packager(options)

    # Download the data
    lang_packager.download()

    # Set format to python to get data back
    lang_packager.options.format = "python"

    # Get the data
    data = lang_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Function to find characters with pronunciation data in multiple languages
    def find_multilingual_chars(
        char_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Find characters with pronunciation data in multiple languages."""
        result: list[dict[str, Any]] = []

        # Process each character
        for char in char_data:
            lang_count = 0

            # Count languages for which we have pronunciation data
            for field in [
                "kMandarin",
                "kJapaneseOn",
                "kKorean",
                "kVietnamese",
                "kCantonese",
            ]:
                if char.get(field):
                    lang_count += 1

            # If this character has pronunciation data in multiple languages, add it
            if lang_count > 1:
                result.append(dict(char))

        return result

    # Convert data to list of dictionaries
    char_data_list = []
    if data is not None:
        char_data_list = [dict(item) for item in data]

    # Find characters with pronunciation data in multiple languages
    multilingual_chars = find_multilingual_chars(char_data_list)

    # Print diagnostic info
    print(f"Found {len(data)} total characters")
    print(
        f"Found {len(multilingual_chars)} characters with "
        f"multiple language pronunciations"
    )

    # Test with multilingual data if available
    if multilingual_chars and multilingual_chars[0]:
        # Look at a sample multilingual character
        sample_char = multilingual_chars[0]
        print(f"Sample character: {sample_char['char']}")

        # Print pronunciation info for the sample character
        if "kMandarin" in sample_char:
            print(f"  Mandarin: {sample_char['kMandarin']}")
        if "kJapaneseOn" in sample_char:
            print(f"  Japanese: {sample_char['kJapaneseOn']}")
        if "kKorean" in sample_char:
            print(f"  Korean: {sample_char['kKorean']}")
        if "kVietnamese" in sample_char:
            print(f"  Vietnamese: {sample_char['kVietnamese']}")
        if "kCantonese" in sample_char:
            print(f"  Cantonese: {sample_char['kCantonese']}")
    else:
        # If no multilingual data is available, just check data structure
        if data is not None:
            for char in data[:5]:
                assert "char" in char
