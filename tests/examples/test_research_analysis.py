#!/usr/bin/env python
"""Example of using unihan-etl for research analysis applications."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from unihan_etl.core import Packager


def test_extract_etymology_data(unihan_quick_packager: Packager) -> None:
    """Test extract and analyze etymology data with UNIHAN."""
    # First download the data
    unihan_quick_packager.download()

    # Set format to python to get data back
    unihan_quick_packager.options.format = "python"

    # Get etymology-specific data
    options = {
        "fields": [
            "kSemanticVariant",
            "kSpecializedSemanticVariant",
            "kZVariant",
            "kSimplifiedVariant",
            "kTraditionalVariant",
        ],
    }

    # Create the packager
    etymology_packager = Packager(options)

    # Download the data
    etymology_packager.download()

    # Set format to python for data export
    etymology_packager.options.format = "python"

    # Get the data
    data: Sequence[Mapping[str, Any]] | None = etymology_packager.export()

    # Verify we have data
    assert data is not None

    # Process the data for research analysis
    variants_data = []

    # Only process if we have data
    if data is not None:
        # Extract semantic variants
        for item in data:
            char = item.get("char", "")

            # Skip if no character
            if not char:
                continue

            variants = {
                "char": char,
                "semantic": item.get("kSemanticVariant", ""),
                "specialized": item.get("kSpecializedSemanticVariant", ""),
                "z_variant": item.get("kZVariant", ""),
                "simplified": item.get("kSimplifiedVariant", ""),
                "traditional": item.get("kTraditionalVariant", ""),
            }

            variants_data.append(variants)

    # Verify we extracted data
    if data is not None:
        assert len(variants_data) > 0
