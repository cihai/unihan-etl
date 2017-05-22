# -*- coding: utf-8 -*-
"""Test expansion of multi-value fields in UNIHAN."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import pytest

from unihan_tabular import process


def test_expands_spaces(expanded_data):
    for item in expanded_data:
        for field in item.keys():
            if field in process.SPACE_DELIMITED_LIST_FIELDS and item[field]:
                assert isinstance(item[field], list)


def test_expand_kCantonese(expanded_data):
    # test kCantonese
    item = [i for i in expanded_data if i['ucn'] == 'U+342B'][0]
    if item['ucn'] == 'U+342B':
        assert set(item['kCantonese']) == set(['gun3', 'hung1', 'zung1'])
    else:
        assert False, "Missing field U+342B kCantonese"


@pytest.mark.parametrize("ucn,field,expected", [
    ("U+37AE", "kJapaneseKun", ['DERU', 'DASU']),
    ("U+37AE", "kJapaneseOn", ['SHUTSU', 'SUI']),
    ("U+37AE", "kDefinition", [
        'variant of 出 U+51FA, to go out, send out',
        'to stand',
        'to produce'
    ]),
])
def test_expand(expanded_data, ucn, field, expected):
    # test kDefinition (split on ;), kJapanese, kJapaneseKun
    item = [i for i in expanded_data if i['ucn'] == ucn][0]
    assert set(item[field]) == set(expected)


def test_expand_kMandarin(expanded_data):
    """
    The most customary pinyin reading for this character. When there are two
    values, then the first is preferred for zh-Hans (CN) and the second is
    preferred for zh-Hant (TW). When there is only one value, it is appropriate
    for both.
    """
    ucn = "U+4FFE"
    item = [i for i in expanded_data if i['ucn'] == ucn][0]
    assert item['kMandarin'] == {
        "zh-Hans": "bǐ",
        "zh-Hant": "bì"
    }
