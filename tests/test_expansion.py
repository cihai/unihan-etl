# -*- coding: utf-8 -*-
"""Test expansion of multi-value fields in UNIHAN."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from unihan_tabular import process


def test_expands_spaces(expanded_data):

    for item in expanded_data:
        for field in item.keys():
            if field in process.SPACE_DELIMITED_FIELDS and item[field]:
                assert isinstance(item[field], list)


def test_expand_kCantonese(expanded_data):
    # test kCantonese
    item = [i for i in expanded_data if i['ucn'] == 'U+342B'][0]
    if item['ucn'] == 'U+342B':
        assert set(item['kCantonese']) == set(['gun3', 'hung1', 'zung1'])
    else:
        assert False, "Missing field U+342B kCantonese"


def test_expand_kDefinition(expanded_data):
    # test kDefinition (split on ;), kJapanese, kJapaneseKun
    item = [i for i in expanded_data if i['ucn'] == 'U+37AE'][0]
    if item['ucn'] == 'U+37AE':
        assert set(item['kJapaneseKun']) == set(['DERU', 'DASU'])
        assert set(item['kJapaneseOn']) == set(['SHUTSU', 'SUI'])
        assert set(item['kDefinition']) == set([
            'variant of 出 U+51FA, to go out, send out',
            'to stand',
            'to produce'
        ])
