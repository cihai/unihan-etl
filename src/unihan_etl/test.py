"""Test helpers functions for downloading and processing Unihan data."""
import typing as t


def assert_dict_contains_subset(
    subset: t.Dict[str, t.Any],
    dictionary: t.Mapping[str, t.Any],
    msg: t.Optional[str] = None,
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
