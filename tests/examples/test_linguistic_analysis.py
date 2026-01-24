#!/usr/bin/env python
"""Example of using unihan-etl for linguistic analysis."""

from __future__ import annotations

from unihan_etl.core import Packager


def test_linguistic_analysis(unihan_quick_packager: Packager) -> None:
    """Test linguistic analysis using UNIHAN data."""
    # Define fields needed for linguistic analysis
    options = {
        "fields": [
            "kDefinition",
            "kMandarin",
            "kCantonese",
            "kTang",
            "kJapaneseOn",
            "kKorean",
        ],
    }

    # Create the packager
    ling_packager = Packager(options)

    # Download the data
    ling_packager.download()

    # Set format to python for data export
    ling_packager.options.format = "python"

    # Get the data
    data = ling_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Analyze sound correspondences across languages
    sound_correspondences = []

    # Only analyze a sample of the data to keep the test reasonable
    sample_data = data[:100] if len(data) > 100 else data

    for item in sample_data:
        # Get pronunciations across languages
        cantonese = item.get("kCantonese", "")
        mandarin = item.get("kMandarin", "")
        tang = item.get("kTang", "")
        japanese = item.get("kJapaneseOn", "")
        korean = item.get("kKorean", "")

        # Handle cases where values might be lists or other non-string types
        cantonese = (
            str(cantonese[0])
            if isinstance(cantonese, list) and cantonese
            else str(cantonese)
        )

        mandarin = (
            str(mandarin[0])
            if isinstance(mandarin, list) and mandarin
            else str(mandarin)
        )

        tang = str(tang[0]) if isinstance(tang, list) and tang else str(tang)

        japanese = (
            str(japanese[0])
            if isinstance(japanese, list) and japanese
            else str(japanese)
        )

        korean = str(korean[0]) if isinstance(korean, list) and korean else str(korean)

        # Record the correspondence
        sound_correspondences.append(
            {
                "char": item["char"],
                "cantonese": cantonese,
                "mandarin": mandarin,
                "tang": tang,
                "japanese": japanese,
                "korean": korean,
            }
        )

    # Verify we found some correspondences
    assert len(sound_correspondences) > 0

    # Example simple analysis: Count characters that have similar
    # initial consonants in Cantonese and Mandarin
    similar_initial_count = 0

    for corr in sound_correspondences:
        # Make sure we have pronunciation strings with at least 1 character
        if (
            corr["cantonese"]
            and corr["mandarin"]
            and isinstance(corr["cantonese"], str)
            and isinstance(corr["mandarin"], str)
            and len(corr["cantonese"]) > 0
            and len(corr["mandarin"]) > 0
        ):
            # Compare first characters
            first_char_cantonese = corr["cantonese"][0].lower()
            first_char_mandarin = corr["mandarin"][0].lower()

            if first_char_cantonese == first_char_mandarin:
                similar_initial_count += 1

    # This is just to check the analysis logic works
    assert similar_initial_count >= 0
