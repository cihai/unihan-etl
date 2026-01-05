#!/usr/bin/env python
"""Example of using unihan-etl for educational tools."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from unihan_etl.core import Packager


def test_character_learning_data(unihan_quick_packager: Packager) -> None:
    """Test extracting character learning data for educational applications."""
    # Download the data
    unihan_quick_packager.download()

    # Set format to python for data export
    unihan_quick_packager.options.format = "python"

    # Get the data
    full_data = unihan_quick_packager.export()

    # Verify we have data
    assert full_data is not None
    assert len(full_data) > 0

    # Define fields relevant for educational applications
    # Using only valid fields available in the Unihan database
    options = {
        "fields": [
            "kTotalStrokes",
            "kGradeLevel",
            "kDefinition",
            "kMandarin",
            "kCantonese",
            "kJapaneseOn",
            "kJapaneseKun",
            "kKorean",
        ],
    }

    # Create a custom packager
    edu_packager = Packager(options)
    edu_packager.download()
    edu_packager.options.format = "python"
    data: Sequence[Mapping[str, Any]] | None = edu_packager.export()

    # Verify we have data
    assert data is not None

    # Create educational data structure
    educational_data = []

    # Process only a sample of characters to keep test short
    sample_size = min(50, len(data))

    for i, item in enumerate(data):
        if i >= sample_size:
            break

        char = item.get("char", "")
        if not char:
            continue

        # Get basic info
        definition = item.get("kDefinition", "")
        grade_level = item.get("kGradeLevel", "")
        strokes = item.get("kTotalStrokes", "")

        # Get pronunciation data
        mandarin = item.get("kMandarin", "")
        cantonese = item.get("kCantonese", "")
        japanese_on = item.get("kJapaneseOn", "")
        japanese_kun = item.get("kJapaneseKun", "")
        korean = item.get("kKorean", "")

        # Convert to strings if needed
        if not isinstance(definition, str):
            definition = str(definition)

        if not isinstance(grade_level, str):
            grade_level = str(grade_level)

        if not isinstance(strokes, str):
            strokes = str(strokes)

        # Create a learning entry
        educational_data.append(
            {
                "character": char,
                "definition": definition,
                "grade_level": grade_level,
                "stroke_count": strokes,
                "pronunciations": {
                    "mandarin": mandarin,
                    "cantonese": cantonese,
                    "japanese_on": japanese_on,
                    "japanese_kun": japanese_kun,
                    "korean": korean,
                },
            }
        )

    # Verify we created some educational data
    assert len(educational_data) > 0
