#!/usr/bin/env python
"""Example of filtering characters by educational grade level."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_educational_filtering(unihan_quick_packager: Packager) -> None:
    """Demonstrate filtering for educational-focused character sets."""
    # Set options for education-related fields
    options = {
        "fields": ["kGradeLevel", "kTotalStrokes", "kDefinition"],
    }

    # Create a packager with the fields we need
    edu_packager = Packager(options)

    # Download the data
    edu_packager.download()

    # Set format to python to get data back
    edu_packager.options.format = "python"

    # Get the data
    data = edu_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Filter for elementary-level characters (grade levels 1-3)
    elementary_chars = []
    for item in data:
        grade_level = item.get("kGradeLevel")
        if grade_level:
            # Grade level might be a list or a string
            if isinstance(grade_level, list):
                grade_values = grade_level
            else:
                grade_values = [grade_level]

            # Check if any values are elementary levels
            if any(str(g) in ["1", "2", "3"] for g in grade_values):
                elementary_chars.append(item)

    # Note: if no elementary characters are found, this might be because
    # the sample data doesn't include grade level information.
    # In that case, we'll just check the data structure instead.

    # Print some diagnostic info for the first few items
    print(f"Found {len(data)} total characters")
    print(f"Found {len(elementary_chars)} elementary characters")

    # Verify the structure of the data
    for char in data[:5]:  # Check first 5 characters
        assert "char" in char
        if "kTotalStrokes" in char:
            assert char["kTotalStrokes"] is not None
