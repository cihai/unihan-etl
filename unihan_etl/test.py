"""Test helpers functions for downloading and processing Unihan data."""
from typing import Any, Dict, Optional


def assert_dict_contains_subset(
    subset: Dict[str, Any],
    dictionary: Dict[str, Any],
    msg: Optional[str] = None,
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
    """
    for key, value in subset.items():
        assert key in dictionary, msg
        assert dictionary[key] == value, msg
