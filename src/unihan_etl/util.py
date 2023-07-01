"""Utilities for parsing UNIHAN's data and structures."""
import re
import sys
import typing as t
from collections.abc import Mapping

if t.TYPE_CHECKING:
    from unihan_etl.types import UntypedUnihanData


def ucn_to_unicode(ucn: str) -> str:
    """Return a python unicode value from a UCN.

    Converts a Unicode Universal Character Number (e.g. ``"U+4E00"`` or ``"4E00"``) to
    Python unicode ``(u'\\u4e00')``

    >>> ucn_to_unicode("U+4E00")
    '\\u4e00'

    >>> ucn_to_unicode("4E00")
    '\\u4e00'
    """
    if isinstance(ucn, str):
        ucn = ucn.strip("U+")
        if len(ucn) > int(4):
            bytechar = rb"\U" + format(int(ucn, 16), "08x").encode("latin1")
            char = bytechar.decode("unicode_escape")
        else:
            char = chr(int(ucn, 16))
    else:
        char = chr(ucn)

    assert isinstance(char, str)

    return char


def ucnstring_to_python(ucn_string: str) -> bytes:
    """Return string with Unicode UCN (e.g. "U+4E00") to native Python Unicode
    (u'\\u4e00').

    >>> ucnstring_to_python("U+4E00")
    b'\xe4\xb8\x80'
    """
    res = re.findall(r"U\+[0-9a-fA-F]*", ucn_string)
    for r in res:
        ucn_string = ucn_string.replace(str(r), str(ucn_to_unicode(r)))

    ucn = ucn_string.encode("utf-8")

    assert isinstance(ucn, bytes)
    return ucn


def ucnstring_to_unicode(ucn_string: str) -> str:
    """Return ucnstring as Unicode.

    >>> ucnstring_to_unicode('U+4E00')
    '一'

    >>> ucnstring_to_unicode('U+4E01')
    '丁'

    >>> ucnstring_to_unicode('U+0030')
    '0'

    >>> ucnstring_to_unicode('U+0031')
    '1'
    """
    ucn_string = ucnstring_to_python(ucn_string).decode("utf-8")

    assert isinstance(ucn_string, str)
    return ucn_string


def _dl_progress(
    count: int, block_size: int, total_size: int, out: t.IO[str] = sys.stdout
) -> None:
    """
    MIT License: https://github.com/okfn/dpm-old/blob/master/dpm/util.py

    Modification for testing: http://stackoverflow.com/a/4220278

    >>> _dl_progress(0, 1, 10)
    Total size: 10b

    >>> _dl_progress(0, 100, 942_200)
    Total size: 942Kb
    """

    def format_size(_bytes: int) -> str:
        if _bytes > 1000 * 1000:
            return "%.1fMb" % (_bytes / 1000.0 / 1000)
        elif _bytes > 10 * 1000:
            return "%iKb" % (_bytes / 1000)
        elif _bytes > 1000:
            return "%.1fKb" % (_bytes / 1000.0)
        else:
            return "%ib" % _bytes

    if not count:
        print("Total size: %s" % format_size(total_size))
    last_percent = int((count - 1) * block_size * 100 / total_size)
    # may have downloaded less if count*block_size > total_size
    maxdownloaded = count * block_size
    percent = min(int(maxdownloaded * 100 / total_size), 100)
    out.flush()
    if percent > last_percent:
        # TODO: is this acceptable? Do we want to do something nicer?
        out.write(
            "%3d%% [%s>%s]\r"
            % (
                percent,
                int(round(percent / 2)) * "=",
                int(round(50 - percent / 2)) * " ",
            )
        )
        out.flush()
    if maxdownloaded >= total_size:
        print("\n")


T = t.TypeVar("T", bound="Mapping[str, t.Any]")


def merge_dict(
    d: T,
    u: T,
) -> T:
    """Return updated dict.

    Parameters
    ----------
    d : dict
    u : dict

    Returns
    -------
    dict :
        Updated dictionary

    Notes
    -----
    Thanks: http://stackoverflow.com/a/3233356
    """
    for k, v in u.items():
        assert isinstance(d, dict)
        if isinstance(v, dict):
            r = merge_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def get_fields(d: "UntypedUnihanData") -> t.List[str]:
    """Return list of fields from dict of {filename: ['field', 'field1']}."""
    return sorted({c for cs in d.values() for c in cs})
