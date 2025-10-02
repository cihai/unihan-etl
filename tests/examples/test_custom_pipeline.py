#!/usr/bin/env python
"""Example of creating a custom processing pipeline with UNIHAN-ETL."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from unihan_etl.core import Packager


def test_custom_pipeline(unihan_quick_packager: Packager) -> None:
    """Demonstrate creating a custom processing pipeline."""
    # Create options for the packager
    options = {
        "fields": ["kDefinition", "kMandarin", "kTotalStrokes"],
        "format": "python",
    }

    # Create a packager with our options
    packager = Packager(options)

    # Download the data
    packager.download()

    # Function to create a custom pipeline
    def custom_unihan_pipeline(options: dict[str, Any]) -> list[dict[str, Any]]:
        """Create a custom pipeline for processing UNIHAN data."""
        # Create a packager with the provided options
        my_packager = Packager(options)

        # Download the UNIHAN data
        my_packager.download()

        # Set format to python to get data in Python format
        my_packager.options.format = "python"

        # Get the raw data
        raw_data = my_packager.export()

        # Process the data with custom logic
        processed_data: list[dict[str, Any]] = []
        if raw_data is not None:
            for item in raw_data:
                # Only include characters with definitions
                if "kDefinition" in item:
                    # Create a new processed item
                    processed_item: dict[str, Any] = {
                        "character": item["char"],
                        "definition": item["kDefinition"],
                        "metadata": {},
                    }

                    # Add pronunciation if available
                    if "kMandarin" in item:
                        processed_item["metadata"]["pronunciation"] = item["kMandarin"]

                    # Add complexity score based on stroke count
                    if "kTotalStrokes" in item:
                        try:
                            strokes = item["kTotalStrokes"]
                            if isinstance(strokes, list):
                                strokes = strokes[0]
                            processed_item["metadata"]["complexity"] = int(strokes)
                        except (ValueError, TypeError, IndexError):
                            processed_item["metadata"]["complexity"] = 0

                    processed_data.append(processed_item)

        return processed_data

    # Call our custom pipeline
    result = custom_unihan_pipeline(options)

    # Verify we have results
    assert result is not None
    assert len(result) > 0

    # Verify the structure of our processed data
    if result:
        for item in result[:5]:  # Check first 5 items
            assert "character" in item
            assert "definition" in item
            assert "metadata" in item
            assert isinstance(item["metadata"], dict)

    # Demonstrate how to output custom processed data to a file
    temp_dir = tempfile.mkdtemp()
    try:
        # Write sample data to a JSON file
        output_file = Path(temp_dir) / "custom_processed.json"

        # Just write the first 10 items for demonstration
        sample_data = result[:10] if len(result) > 10 else result

        with output_file.open("w", encoding="utf8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        # Verify file was created
        assert output_file.exists()
        print(f"Sample data written to: {output_file}")

        # Clean up
        output_file.unlink()
        Path(temp_dir).rmdir()
    except OSError:
        # Ignore cleanup errors
        pass
