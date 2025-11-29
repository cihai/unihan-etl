#!/usr/bin/env python
"""Example of working with UNIHAN field metadata."""

from __future__ import annotations

from typing import Any

from unihan_etl.constants import UNIHAN_FIELDS, UNIHAN_MANIFEST


def test_unihan_fields() -> None:
    """Test accessing UNIHAN fields metadata."""
    # Verify UNIHAN_FIELDS exists and has data
    assert UNIHAN_FIELDS is not None
    assert len(UNIHAN_FIELDS) > 0

    # Check some common fields exist
    assert "kDefinition" in UNIHAN_FIELDS
    assert "kMandarin" in UNIHAN_FIELDS
    assert "kCantonese" in UNIHAN_FIELDS

    # Get field file mapping information
    file_mapping: dict[str, dict[str, Any]] = {}

    # Build a dictionary of fields to their files
    for filename, fields in UNIHAN_MANIFEST.items():
        for field in fields:
            if field not in file_mapping:
                file_mapping[field] = {
                    "file": filename,
                }

    # Verify structure of field metadata
    assert "kDefinition" in file_mapping
    assert "file" in file_mapping["kDefinition"]

    # Verify kCantonese is in a certain file
    assert "kCantonese" in file_mapping
    assert "file" in file_mapping["kCantonese"]
    assert "Unihan_Readings.txt" in file_mapping["kCantonese"]["file"]

    # Count fields per file
    fields_per_file = {}
    for filename, fields in UNIHAN_MANIFEST.items():
        fields_per_file[filename] = len(fields)

    # Verify we have field counts
    assert len(fields_per_file) > 0
