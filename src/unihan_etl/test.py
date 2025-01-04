"""Test helpers functions for downloading and processing Unihan data."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from collections.abc import Mapping


def assert_dict_contains_subset(
    subset: dict[str, t.Any],
    dictionary: Mapping[str, t.Any],
    msg: str | None = None,
) -> None:
    """
    Ported assertion for dict subsets in py.test.

    Parameters
    ----------
    subset : dict
        needle
    dictionary : dict
        haystack
    msg : str, optional
        message display if assertion fails

    >>> assert_dict_contains_subset({ 'test': 3 }, { 'more_data': '_', 'test': 3 })

    >>> not assert_dict_contains_subset({ 'test': 3 }, { 'more_data': '_', 'test': 4 })
    Traceback (most recent call last):
        ...
    AssertionError: None
    """
    for key, value in subset.items():
        assert key in dictionary, msg
        assert dictionary[key] == value, msg
