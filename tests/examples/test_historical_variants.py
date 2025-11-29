#!/usr/bin/env python
"""Example of analyzing historical character variants with UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_historical_variants(unihan_quick_packager: Packager) -> None:
    """Demonstrate analyzing historical character variants."""
    # Set options for historical variant fields
    options = {
        "fields": ["kSemanticVariant", "kZVariant", "kSpecializedSemanticVariant"],
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

    # Function to find characters with multiple historical variants
    def find_chars_with_multiple_variants(
        char_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Find characters with multiple historical variants."""
        result: list[dict[str, Any]] = []

        # Process each character
        for char in char_data:
            variant_count = 0

            # Count different types of variants
            if "kSemanticVariant" in char:
                is_list = isinstance(char["kSemanticVariant"], list)
                variant_count += len(char["kSemanticVariant"]) if is_list else 1

            if "kZVariant" in char:
                is_list = isinstance(char["kZVariant"], list)
                variant_count += len(char["kZVariant"]) if is_list else 1

            if "kSpecializedSemanticVariant" in char:
                is_list = isinstance(char["kSpecializedSemanticVariant"], list)
                count = len(char["kSpecializedSemanticVariant"]) if is_list else 1
                variant_count += count

            # If this character has multiple variants, add it to our result
            if variant_count > 1:
                result.append(dict(char))

        return result

    # Convert data to list of dictionaries if necessary
    char_data_list = []
    if data is not None:
        char_data_list = [dict(item) for item in data]

    # Find characters with multiple variants
    multiple_variants = find_chars_with_multiple_variants(char_data_list)

    # Print diagnostic info
    print(f"Found {len(data)} total characters")
    print(f"Found {len(multiple_variants)} characters with multiple variants")

    # Test with variant data if available
    if multiple_variants:
        # Look at a sample character with multiple variants
        sample_char = multiple_variants[0]
        print(f"Sample character: {sample_char['char']}")

        # Print variant info for the sample character
        if "kSemanticVariant" in sample_char:
            print(f"  Semantic variants: {sample_char['kSemanticVariant']}")
        if "kZVariant" in sample_char:
            print(f"  Z-variants: {sample_char['kZVariant']}")
        if "kSpecializedSemanticVariant" in sample_char:
            print(
                f"  Specialized semantic variants: "
                f"{sample_char['kSpecializedSemanticVariant']}"
            )
    else:
        # If no variant data is available, just check data structure
        if data is not None:
            for char in data[:5]:
                assert "char" in char
