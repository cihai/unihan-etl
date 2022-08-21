"""Utility and helper methods for script.

util
~~~~

"""
import re
import sys
import typing as t


def ucn_to_unicode(ucn: str) -> str:
    """Return a python unicode value from a UCN.

    Converts a Unicode Universal Character Number (e.g. "U+4E00" or "4E00") to
    Python unicode (u'\\u4e00')"""
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
    """
    res = re.findall(r"U\+[0-9a-fA-F]*", ucn_string)
    for r in res:
        ucn_string = ucn_string.replace(str(r), str(ucn_to_unicode(r)))

    ucn = ucn_string.encode("utf-8")

    assert isinstance(ucn, bytes)
    return ucn


def ucnstring_to_unicode(ucn_string: str) -> str:
    """Return ucnstring as Unicode."""
    ucn_string = ucnstring_to_python(ucn_string).decode("utf-8")

    assert isinstance(ucn_string, str)
    return ucn_string


def _dl_progress(
    count: int, block_size: int, total_size: int, out: t.IO[str] = sys.stdout
) -> None:
    """
    MIT License: https://github.com/okfn/dpm-old/blob/master/dpm/util.py

    Modification for testing: http://stackoverflow.com/a/4220278

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


_T = t.TypeVar("_T")


def merge_dict(
    base: t.Mapping[str, _T], additional: t.Mapping[str, _T]
) -> t.Dict[str, _T]:
    if base is None:
        return additional

    if additional is None:
        return base

    if not (isinstance(base, t.Mapping) and isinstance(additional, t.Mapping)):
        return additional

    merged = base
    assert isinstance(merged, dict)

    for key, value in additional.items():
        if isinstance(value, t.Mapping):
            assert isinstance(key, str)
            assert isinstance(value, dict)
            merged.setdefault(key, {})
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value

    return merged
