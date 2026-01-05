#!/usr/bin/env python
"""Example of integrating unihan-etl with database systems."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

from unihan_etl.core import Packager


def test_database_population(unihan_quick_packager: Packager) -> None:
    """Test database population with UNIHAN data."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create a table for the UNIHAN data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS unihan (
            char TEXT PRIMARY KEY,
            ucn TEXT,
            kDefinition TEXT,
            kMandarin TEXT
        )
        """)

        # Get UNIHAN data for database
        options = {
            "fields": ["kDefinition", "kMandarin"],
        }

        # Create a packager with the fields we need
        db_packager = Packager(options)

        # Download the data
        db_packager.download()

        # Set format to python to get data back
        db_packager.options.format = "python"

        # Get the data
        data = db_packager.export()

        # Verify we have data
        assert data is not None
        assert len(data) > 0

        # Insert data into database
        for item in data:
            # Convert lists or dicts to strings if needed
            definition = item.get("kDefinition", "")
            if isinstance(definition, (list, dict)):
                definition = str(definition)

            mandarin = item.get("kMandarin", "")
            if isinstance(mandarin, (list, dict)):
                mandarin = str(mandarin)

            cursor.execute(
                "INSERT INTO unihan (char, ucn, kDefinition, kMandarin) "
                "VALUES (?, ?, ?, ?)",
                (item["char"], item["ucn"], definition, mandarin),
            )

        # Commit changes
        conn.commit()

        # Verify data was inserted
        cursor.execute("SELECT COUNT(*) FROM unihan")
        count = cursor.fetchone()[0]

        # Verify we have data
        assert count > 0

        # Verify we can query the database
        cursor.execute("SELECT * FROM unihan LIMIT 1")
        row = cursor.fetchone()

        # Check structure of the row
        assert row is not None
        assert len(row) == 4  # char, ucn, kDefinition, kMandarin

    finally:
        # Clean up
        conn.close()
        os.close(db_fd)
        Path(db_path).unlink()
