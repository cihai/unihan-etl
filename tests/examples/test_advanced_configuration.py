#!/usr/bin/env python
"""Example of using advanced configuration options with UNIHAN-ETL."""

from __future__ import annotations

import tempfile
from pathlib import Path

from unihan_etl.core import Packager


def test_advanced_configuration(unihan_quick_packager: Packager) -> None:
    """Demonstrate using advanced configuration options."""
    # Get a temporary directory for outputs
    temp_dir = tempfile.mkdtemp()
    temp_file = Path(temp_dir) / "output.json"

    # Set up advanced options
    options = {
        "fields": ["kDefinition", "kCantonese", "kMandarin", "kTotalStrokes"],
        "destination": str(temp_file),
        "format": "json",
        "expand": True,
        "prune_empty": True,
    }

    # Create a packager with advanced configuration
    adv_packager = Packager(options)

    # Download the data
    adv_packager.download()

    # Export to specified format (JSON)
    adv_packager.export()

    # Verify the output file was created
    assert temp_file.exists()

    # Demonstrate accessing configuration attributes
    print(f"Output format: {adv_packager.options.format}")
    print(f"Fields: {adv_packager.options.fields}")
    print(f"Output file: {adv_packager.options.destination}")
    print(f"Expand: {adv_packager.options.expand}")
    print(f"Prune empty: {adv_packager.options.prune_empty}")

    # For demonstration, let's reconfigure for a CSV output
    csv_file = Path(temp_dir) / "output.csv"

    # Create new packager with CSV format
    csv_options = options.copy()
    csv_options.update({"format": "csv", "destination": str(csv_file)})

    csv_packager = Packager(csv_options)

    # Download and process
    csv_packager.download()
    csv_packager.export()

    # Verify CSV file was created
    assert csv_file.exists()

    # Clean up temp files
    try:
        temp_file.unlink()
        csv_file.unlink()
        Path(temp_dir).rmdir()
    except OSError:
        # Ignore cleanup errors
        pass
