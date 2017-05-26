# -*- coding: utf8 -*-
"""Functions to uncompact details inside field values."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import re
from unihan_tabular.constants import SPACE_DELIMITED_FIELDS


def expand_field(field, fvalue):
    """Return structured value of information in UNIHAN field

    :param field: field name
    :type field: str
    :param fvalue: value of field
    :type favalue: str
    :returns: list or dict of expanded field information per UNIHAN's
        documentation
    :rtype: list or dict
    """
    if field in SPACE_DELIMITED_FIELDS and fvalue:
        fvalue = fvalue.split(' ')
    if field == 'kDefinition':
        fvalue = [c.strip() for c in fvalue.split(';')]
    if field == 'kMandarin':
        cn = fvalue[0]
        if len(fvalue) == 1:
            tw = fvalue[0]
        else:
            tw = fvalue[1]
        fvalue = {
            "zh-Hans": cn,
            "zh-Hant": tw
        }
    if field == 'kTotalStrokes':
        cn = fvalue[0]
        if len(fvalue) == 1:
            tw = fvalue[0]
        else:
            tw = fvalue[1]
        fvalue = {
            "zh-Hans": int(cn),
            "zh-Hant": int(tw)
        }
    if field == 'kHanYu':
        for i, value in enumerate(fvalue):
            fvalue[i] = {
                "volume": int(value[0]),
                "page": int(value[1:5]),
                "character": int(value[6:8]),
                "virtual": int(value[8])
            }
    if field == 'kHanyuPinyin':
        for i, value in enumerate(fvalue):
            value = [c.strip() for c in value.split(':')]
            fvalue[i] = {
                "locations": value[0],
                "readings": value[1]
            }
            for k, v in fvalue[i].items():
                fvalue[i][k] = v.split(',')
                if k == "locations":
                    for ii, vvalue in enumerate(fvalue[i][k]):
                        fvalue[i][k][ii] = {
                            "volume": int(vvalue[0]),
                            "page": int(vvalue[1:5]),
                            "character": int(vvalue[6:8]),
                            "virtual": int(vvalue[8])
                        }
    if field == 'kXHC1983':
        for i, value in enumerate(fvalue):
            vals = value.split(':')
            fvalue[i] = {
                "locations": vals[0],
                "reading": vals[1],
            }
            for k, v in fvalue[i].items():
                if k == "locations":
                    fvalue[i][k] = v.split(',')
                    for ii, vvalue in enumerate(fvalue[i][k]):
                        valz = vvalue.split('.')
                        substituted = valz[1][-1] == "*"
                        valz[1] = valz[1].replace("*", '')
                        fvalue[i][k][ii] = {
                            "page": int(valz[0]),
                            "position": int(valz[1][0:2]),
                            "entry": int(valz[1][2]),
                            "substituted": substituted
                        }
    if field == 'kCheungBauer':
        for i, value in enumerate(fvalue):
            value = [c.strip() for c in value.split(';')]
            fvalue[i] = {
                "radical": int(value[0].split('/')[0]),
                "strokes": int(value[0].split('/')[1]),
                "cangjie": value[1] or None,
                "readings": value[2].split(',')
            }
    if field == 'kRSAdobe_Japan1_6':
        for i, value in enumerate(fvalue):
            vals = value.split('+')
            fvalue[i] = {
                "type": vals[0],
                "cid": int(vals[1]),
                "radical": int(vals[2].split('.')[0]),
                "strokes": int(vals[2].split('.')[1]),
                "strokes-residue": int(vals[2].split('.')[2])
            }
    if field == 'kCihaiT':
        for i, value in enumerate(fvalue):
            vals = value.split('.')
            fvalue[i] = {
                "page": int(vals[0]),
                "row": int(vals[1][0]),
                "position": int(vals[1][1:3]),
            }
    if field == 'kDaeJaweon':
        vals = fvalue.split('.')
        fvalue = {
            "page": int(vals[0]),
            "position": int(vals[1][0:2]),
            "virtual": int(vals[1][2]),
        }
    if field == 'kFenn':
        for i, value in enumerate(fvalue):
            v = re.split(r'(\d+)(\w+)', fvalue[i])
            fvalue[i] = {
                "phonetic": int(v[1]),
                "frequency": v[2]
            }
    if field == 'kHanyuPinlu':
        for i, value in enumerate(fvalue):
            v = fvalue[i]
            fvalue[i] = {
                "phonetic": v[0:v.find("(")],
                "frequency": int(v[v.find("(")+1:v.find(")")])
            }
    if field == 'kHDZRadBreak':
        rad, loc = fvalue.split(':')

        fvalue = {
            "radical": rad.split('[')[0],
            "ucn": rad.split('[')[1].replace(']', ''),
            "location": loc
        }
    if field == 'kSBGY':
        for i, value in enumerate(fvalue):
            vals = value.split('.')
            fvalue[i] = {
                "page": int(vals[0]),
                "character": int(vals[1])
            }
    if field == 'kRSUnicode':
        for i, value in enumerate(fvalue):
            vals = value.split('.')
            simp = vals[0][-1] == "'"
            fvalue[i] = {
                "radical": int(vals[0].replace("'", '')),
                "strokes": int(vals[1]),
                "simplified": simp
            }

    if any(field == f for f in [
        'kRSJapanese',
        'kRSKangXi',
        'kRSKanWa',
        'kRSKorean',
    ]):
        for i, value in enumerate(fvalue):
            vals = value.split('.')
            fvalue[i] = {
                "radical": int(vals[0]),
                "strokes": int(vals[1]),
            }
    return fvalue
