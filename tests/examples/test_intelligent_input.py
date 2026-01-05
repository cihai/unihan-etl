#!/usr/bin/env python
"""Example of creating an intelligent character suggestion system with UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_intelligent_character_suggestion(unihan_quick_packager: Packager) -> None:
    """Demonstrate creating an intelligent character suggestion system."""
    # Set options for pronunciation data (note: kFrequency is not in standard UNIHAN)
    options = {
        "fields": ["kMandarin", "kTotalStrokes"],
    }

    # Create a packager with the fields we need
    pinyin_packager = Packager(options)

    # Download the data
    pinyin_packager.download()

    # Set format to python to get data back
    pinyin_packager.options.format = "python"

    # Get the data
    data = pinyin_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Create a mapping of pinyin to characters
    pinyin_to_chars: dict[str, list[str]] = {}
    character_frequency: dict[str, float] = {}  # Changed from int to float

    # Helper function to add pinyin data
    def add_to_chars_dict(pinyin: Any, char: str) -> None:
        # Convert potential complex structures to strings
        if isinstance(pinyin, list):
            for p in pinyin:
                add_to_chars_dict(p, char)
            return

        if pinyin:
            pinyin = str(pinyin)
            if pinyin not in pinyin_to_chars:
                pinyin_to_chars[pinyin] = []
            pinyin_to_chars[pinyin].append(char)

    for item in data:
        char = item["char"]
        # Get pronunciation if available
        if "kMandarin" in item:
            add_to_chars_dict(item["kMandarin"], char)

        # Mock frequency data based on stroke count
        # In a real application, you would use actual frequency data
        if "kTotalStrokes" in item:
            try:
                strokes = item["kTotalStrokes"]
                if isinstance(strokes, list):
                    strokes = strokes[0]
                strokes_int = int(strokes)
                # Simple formula: more strokes generally means less frequent
                character_frequency[char] = max(1.0, 10.0 - strokes_int / 4.0)
            except (ValueError, TypeError, IndexError):
                character_frequency[char] = 1.0

    # Print some diagnostics
    print(f"Found {len(data)} total characters")
    print(f"Found {len(pinyin_to_chars)} unique pronunciations")

    # Example of a function to suggest characters
    def suggest_characters(pinyin: str, context: str | None = None) -> list[str]:
        candidates = pinyin_to_chars.get(pinyin, [])

        # If we have context, prioritize characters that form common words
        # This is a simplified example - in real use you would use a language model
        if context and candidates:
            # Mock function for testing - in reality, you would use a language model
            return sorted(
                candidates,
                key=lambda c: mock_score_in_context(c, context),
                reverse=True,
            )

        # Otherwise sort by frequency
        return sorted(candidates, key=lambda c: character_frequency.get(c, 1.0))

    # Mock function for testing
    def mock_score_in_context(char: str, context: str) -> float:
        # This is just a placeholder - in a real system you would use
        # a language model to score the likelihood of characters in context
        return character_frequency.get(char, 1.0)

    # Test the function if we have pronunciation data
    if pinyin_to_chars:
        test_pinyin = next(iter(pinyin_to_chars))
        suggested = suggest_characters(test_pinyin)
        assert len(suggested) > 0

        # Demonstrate context-based suggestions
        suggested_with_context = suggest_characters(test_pinyin, "test context")
        assert len(suggested_with_context) > 0
