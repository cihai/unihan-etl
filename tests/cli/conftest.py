"""Pytest fixtures for CLI tests."""

from __future__ import annotations

import pytest

from unihan_etl.cli._colors import ColorMode, Colors


@pytest.fixture
def colors_always() -> Colors:
    """Return Colors instance with ALWAYS mode."""
    return Colors(ColorMode.ALWAYS)


@pytest.fixture
def colors_never() -> Colors:
    """Return Colors instance with NEVER mode."""
    return Colors(ColorMode.NEVER)


@pytest.fixture
def colors_auto() -> Colors:
    """Return Colors instance with AUTO mode."""
    return Colors(ColorMode.AUTO)
