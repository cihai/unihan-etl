#!/usr/bin/env python
"""Example of creating a multilingual character lookup system with UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_multilingual_lookup(unihan_quick_packager: Packager) -> None:
    """Demonstrate creating a multilingual character lookup system."""
    # Set options for pronunciation fields
    options = {
        "fields": ["kMandarin", "kCantonese", "kJapaneseOn", "kKorean"],
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

    # Create language-specific pronunciation mappings
    kMandarin_data: dict[str, list[str]] = {}
    kCantonese_data: dict[str, list[str]] = {}
    kJapaneseOn_data: dict[str, list[str]] = {}
    kKorean_data: dict[str, list[str]] = {}

    # Helper function to add pronunciation data
    def add_to_dict(
        pronunciation_dict: dict[str, list[str]], pronunciation: Any, char: str
    ) -> None:
        # Convert potential complex structures to strings
        if isinstance(pronunciation, list):
            for p in pronunciation:
                add_to_dict(pronunciation_dict, p, char)
            return

        if pronunciation:
            pronunciation_str = str(pronunciation)
            if pronunciation_str not in pronunciation_dict:
                pronunciation_dict[pronunciation_str] = []
            pronunciation_dict[pronunciation_str].append(char)

    if data is not None:
        for item in data:
            char = item["char"]

            # Add to appropriate language mappings
            if "kMandarin" in item:
                add_to_dict(kMandarin_data, item["kMandarin"], char)

            if "kCantonese" in item:
                add_to_dict(kCantonese_data, item["kCantonese"], char)

            if "kJapaneseOn" in item:
                add_to_dict(kJapaneseOn_data, item["kJapaneseOn"], char)

            if "kKorean" in item:
                add_to_dict(kKorean_data, item["kKorean"], char)

    # Print some diagnostics
    print(f"Found {len(data)} total characters")
    print(f"Mandarin pronunciations: {len(kMandarin_data)}")
    print(f"Cantonese pronunciations: {len(kCantonese_data)}")
    print(f"Japanese On pronunciations: {len(kJapaneseOn_data)}")
    print(f"Korean pronunciations: {len(kKorean_data)}")

    # Create a mapping of language to pronunciation data
    lang_to_pronunciation = {
        "mandarin": kMandarin_data,
        "cantonese": kCantonese_data,
        "japanese": kJapaneseOn_data,
        "korean": kKorean_data,
    }

    # Function to look up characters by pronunciation in different languages
    def lookup_character(pronunciation: str, language: str = "mandarin") -> list[str]:
        pronunciation_data = lang_to_pronunciation.get(language, {})
        return pronunciation_data.get(pronunciation, [])

    # Test the function with available data
    has_data = False
    for lang, data_dict in lang_to_pronunciation.items():
        if data_dict:
            has_data = True
            test_pronunciation = next(iter(data_dict))
            results = lookup_character(test_pronunciation, lang)
            assert len(results) > 0
            print(
                f"Testing {lang}: Found {len(results)} characters for "
                f"pronunciation '{test_pronunciation}'"
            )

    # If we don't have pronunciation data in test fixture, just verify data structure
    if not has_data and data is not None:
        for char in data[:5]:
            assert "char" in char
