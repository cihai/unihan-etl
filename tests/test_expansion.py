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


@pytest.mark.parametrize("ucn,expected", [
    ("U+346E", {  # U+346E	kMandarin	hún
        "zh-Hans": "hún",
        "zh-Hant": "hún"
    }),
    ("U+4FFE", {  # U+4FFE	kMandarin	bǐ bì
        "zh-Hans": "bǐ",
        "zh-Hant": "bì"
    })
])
def test_expand_kMandarin(expanded_data, ucn, expected):
    """
    The most customary pinyin reading for this character. When there are two
    values, then the first is preferred for zh-Hans (CN) and the second is
    preferred for zh-Hant (TW). When there is only one value, it is appropriate
    for both.
    """
    item = [i for i in expanded_data if i['ucn'] == ucn][0]
    assert item['kMandarin'] == expected


@pytest.mark.parametrize("ucn,expected", [
    ("U+5EFE", [{  # U+5EFE	kHanyuPinyin	10513.110,10514.010,10514.020:gǒng
        "locations": [
            "10513.110",
            "10514.010",
            "10514.020"
        ],
        "readings": [
            "gǒng"
        ]
    }]),
    ("U+5364", [{  # U+5364	kHanyuPinyin	10093.130:xī,lǔ 74609.020:lǔ,xī
        "locations": [
            "10093.130"
        ],
        "readings": [
            "xī",
            "lǔ"
        ]
    }, {
        "locations": [
            "74609.020"
        ],
        "readings": [
            "lǔ",
            "xī"
        ]
    }]),
    ("U+34D8", [{  # U+34D8	kHanyuPinyin	10278.080,10278.090:sù
        "locations": [
            "10278.080",
            "10278.090"
        ],
        "readings": [
            "sù"
        ]
    }]),
    ("U+34CE", [{  # U+34CE	kHanyuPinyin	10297.260:qīn,qìn,qǐn
        "locations": [
            "10297.260"
        ],
        "readings": [
            "qīn", "qìn", "qǐn"
        ]
    }])
])
def test_expand_kHanyuPinyin(expanded_data, ucn, expected):
    """
    Each location has the form “ABCDE.XYZ” (as in “kHanYu”); multiple
    locations for a given pīnyīn reading are separated by “,” (comma). The
    list of locations is followed by “:” (colon), followed by a
    comma-separated list of one or more pīnyīn readings. Where multiple
    pīnyīn readings are associated with a given mapping, these are ordered as
    in HDZ (for the most part reflecting relative commonality). The following
    are representative records.

    | U+34CE | 㓎 | 10297.260: qīn,qìn,qǐn |
    | U+34D8 | 㓘 | 10278.080,10278.090: sù |
    | U+5364 | 卤 | 10093.130: xī,lǔ 74609.020: lǔ,xī |
    | U+5EFE | 廾 | 10513.110,10514.010,10514.020: gǒng |

    For example, the “kHanyuPinyin” value for 卤 U+5364 is
    10093.130: xī,lǔ 74609.020: lǔ,xī”. This means that 卤 U+5364 is found in
    kHanYu” at entries 10093.130 and 74609.020. The former entry has the two
    pīnyīn readings xī and lǔ (in that order), whereas the latter entry has
    the readings lǔ and xī (reversing the order).
    """
    item = [i for i in expanded_data if i['ucn'] == ucn][0]
    assert item['kHanyuPinyin'] == expected


@pytest.mark.parametrize("ucn,expected", [
    ("U+34B9", [{  # U+34B9	kHanYu	10254.060 10254.100
        "volume": 1,
        "page": 254,
        "character": 60
    }, {
        "volume": 1,
        "page": 254,
        "character": 100
    }]),
    ('U+34AD', [{  # U+34AD	kHanYu	10273.120
        "volume": 1,
        "page": 273,
        "character": 120
    }])
])
def test_expand_HanYu(expanded_data, ucn, expected):
    """
    The character references are given in the form “ABCDE.XYZ”, in which: “A”
    is the volume number [1..8]; “BCDE” is the zero-padded page number
    [0001..4809]; “XY” is the zero-padded number of the character on the page
    [01..32]; “Z” is “0” for a character actually in the dictionary, and
    greater than 0 for a character assigned a “virtual” position in the
    dictionary. For example, 53024.060 indicates an actual HDZ character, the
    6th character on Page 3,024 of Volume 5 (i.e. 籉 [U+7C49]). Note that the
    Volume 8 “BCDE” references are in the range [0008..0044] inclusive,
    referring to the pagination of the “Appendix of Addendum” at the end of
    that volume (beginning after p. 5746).

    The first character assigned a given virtual position has an index ending
    in 1; the second assigned the same virtual position has an index ending in
    2; and so on.
    """
    item = [i for i in expanded_data if i['ucn'] == ucn][0]
    assert item['kHanYu'] == expected
