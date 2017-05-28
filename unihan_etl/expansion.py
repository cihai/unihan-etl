# -*- coding: utf8 -*-
"""Functions to uncompact details inside field values.

.. note::

    :func:`re.compile` operations are inside of expand functions:

        1. readability
        2. module-level function bytecode is cached in python
        3. the last used compiled regexes are cached
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import re
import zhon.pinyin
import zhon.hanzi

from unihan_etl.constants import SPACE_DELIMITED_FIELDS

#: IRG G Sources from http://www.unicode.org/reports/tr38/#kIRG_GSource
IRG_G_SOURCES = {
    'G0': 'GB2312-80',
    'G1': 'GB12345-90',
    'G3': 'GB7589-87 unsimplified forms',
    'G5': 'GB7590-87 unsimplified forms',
    'G7': ('General Purpose Hanzi List for Modern Chinese Language, and ',
           'General List of Simplified Hanzi'),
    'GS': 'Singapore Characters',
    'G8': 'GB8565-88',
    'G9': 'GB18030-2000',
    'GE': 'GB16500-95',
    'G4K': 'Siku Quanshu (四庫全書)',
    'GBK': 'Chinese Encyclopedia (中國大百科全書)',
    'GCH': 'Ci Hai (辞海)',
    'GCY': 'Ci Yuan (辭源)',
    'GCYY ': (
        'Chinese Academy of Surveying and Mapping Ideographs '
        '(中国测绘科学院用字)'
    ),
    'GDZ': 'Geographic Publishing House Ideographs (地质出版社用字)',
    'GFZ': 'Founder Press System (方正排版系统)',
    'GGH': 'Gudai Hanyu Cidian (古代汉语词典)',
    'GH': 'GB/T 15564-1995',
    'GHC': 'Hanyu Dacidian (漢語大詞典)',
    'GHZ': 'Hanyu Dazidian ideographs (漢語大字典)',
    'GIDC': 'ID system of the Ministry of Public Security of China, 2009',
    'GJZ': 'Commercial Press Ideographs (商务印书馆用字)',
    'GK': 'GB 12052-89',
    'GKX': (
        'Kangxi Dictionary ideographs (康熙字典) 9th edition (1958) '
        'including the addendum (康熙字典)補遺'
    ),
    'GRM': 'People’s Daily Ideographs (人民日报用字)',
    'GWZ': (
        'Hanyu Dacidian Publishing House Ideographs (漢語大詞典出版社用字)'
    ),
    'GXC': 'Xiandai Hanyu Cidian (现代汉语词典)',
    'GXH': 'Xinhua Zidian (新华字典)',
    'GZFY': 'Hanyu Fangyan Dacidian (汉语方言大词典)',
    'GZH': 'ZhongHua ZiHai (中华字海)',
    'GZJW': 'Yinzhou Jinwen Jicheng Yinde (殷周金文集成引得)',
    'GFC': (
        'Modern Chinese Standard Dictionary (现代汉语规范词典第二版。主编:李'
        '行健。北京:外语 教学与研究出版社) 2010, ISBN:978-7-5600-9518-9'
    ),
    'GGFZ': 'Tongyong Guifan Hanzi Zidian (通用规范汉字字典)'
}


def expand_kDefinition(value):
    return [c.strip() for c in value.split(';')]


def expand_kMandarin(value):
    cn = value[0]
    if len(value) == 1:
        tw = value[0]
    else:
        tw = value[1]
    return {
        "zh-Hans": cn,
        "zh-Hant": tw
    }


def expand_kTotalStrokes(value):
    cn = value[0]
    if len(value) == 1:
        tw = value[0]
    else:
        tw = value[1]
    return {
        "zh-Hans": int(cn),
        "zh-Hant": int(tw)
    }


def expand_kHanYu(value):
    for i, v in enumerate(value):
        value[i] = {
            "volume": int(v[0]),
            "page": int(v[1:5]),
            "character": int(v[6:8]),
            "virtual": int(v[8])
        }
    return value


def expand_kHanyuPinyin(value):
    location_pattern = re.compile(r"""
        (?P<volume>[1-8])
        (?P<page>[0-9]{4})\.
        (?P<character>[0-3][0-9])
        (?P<virtual>[0-3])
    """, re.X)

    for i, v in enumerate(value):
        v = [s.split(',') for s in v.split(':')]
        value[i] = {
            "locations": v[0],
            "readings": v[1]
        }

        for n, loc in enumerate(value[i]['locations']):
            m = location_pattern.match(loc).groupdict()
            value[i]['locations'][n] = {
                "volume": int(m['volume']),
                "page": int(m['page']),
                "character": int(m['character']),
                "virtual": int(m['virtual'])
            }
    return value


def expand_kXHC1983(value):
    pattern = re.compile(r"""
        (?P<page>[0-9]{4})\.
        (?P<position>[0-9]{2})
        (?P<entry>[0-9]{1})
        (?P<substituted>\*?)
    """, re.X)

    for i, v in enumerate(value):
        vals = v.split(':')
        value[i] = {
            "locations": vals[0].split(','),
            "reading": vals[1],
        }

        for n, loc in enumerate(value[i]['locations']):
            m = pattern.match(loc).groupdict()
            value[i]['locations'][n] = {
                "page": int(m['page']),
                "position": int(m['position']),
                "entry": int(m['entry']),
                "substituted": m['substituted'] == "*"
            }
    return value


def expand_kCheungBauer(value):
    pattern = re.compile(r"""
        (?P<radical>[0-9]{3})\/(?P<strokes>[0-9]{2});
        (?P<cangjie>[A-Z]*);
        (?P<readings>[a-z1-6\[\]\/,]+)
    """, re.X)
    for i, v in enumerate(value):
        m = pattern.match(v).groupdict()
        value[i] = {
            "radical": int(m['radical']),
            "strokes": int(m['strokes']),
            "cangjie": m['cangjie'] or None,
            "readings": m['readings'].split(',')
        }
    return value


def expand_kRSAdobe_Japan1_6(value):
    pattern = re.compile(r"""
        (?P<type>[CV])\+
        (?P<cid>[0-9]{1,5})\+
        (?P<radical>[1-9][0-9]{0,2})\.
        (?P<strokes>[1-9][0-9]?)\.
        (?P<strokes_residue>[0-9]{1,2})
    """, re.X)

    for i, v in enumerate(value):
        m = pattern.match(v).groupdict()

        value[i] = {
            "type": m['type'],
            "cid": int(m['cid']),
            "radical": int(m['radical']),
            "strokes": int(m['strokes']),
            "strokes-residue": int(m['strokes_residue'])
        }
    return value


def expand_kCihaiT(value):
    for i, v in enumerate(value):
        vals = v.split('.')
        value[i] = {
            "page": int(vals[0]),
            "row": int(vals[1][0]),
            "position": int(vals[1][1:3]),
        }
    return value


def expand_kDaeJaweon(value):
    pattern = re.compile(r"""
        (?P<page>[0-9]{4})\.
        (?P<position>[0-9]{2})
        (?P<virtual>[01])
    """, re.X)
    m = pattern.match(value).groupdict()

    value = {
        "page": int(m['page']),
        "position": int(m['position']),
        "virtual": int(m['virtual']),
    }
    return value


def expand_kFenn(value):
    pattern = re.compile(r"""
        (?P<phonetic>[0-9]+a?)
        (?P<frequency>[A-KP*])
    """, re.X)

    for i, v in enumerate(value):
        m = pattern.match(v).groupdict(v)
        value[i] = {
            "phonetic": int(m['phonetic']),
            "frequency": m['frequency']
        }
    return value


def expand_kHanyuPinlu(value):
    pattern = re.compile(r"""
        (?P<phonetic>[a-z{}]+)
        \((?P<frequency>[0-9]+)\)
    """.format(zhon.pinyin.lowercase), re.X)

    for i, v in enumerate(value):
        m = pattern.match(v).groupdict()
        value[i] = {
            "phonetic": m['phonetic'],
            "frequency": int(m['frequency'])
        }
    return value


def expand_kHDZRadBreak(value):
    rad, loc = value.split(':')

    pattern = re.compile(r"""
        (?P<radical>[{}]+)
        \[(?P<ucn>U\+2F[0-9A-D][0-9A-F])\]
    """.format(zhon.hanzi.radicals), re.X)
    m = pattern.match(rad).groupdict()

    return {
        "radical": m['radical'],
        "ucn": m['ucn'],
        "location": loc
    }


def expand_kSBGY(value):
    for i, v in enumerate(value):
        vals = v.split('.')
        value[i] = {
            "page": int(vals[0]),
            "character": int(vals[1])
        }
    return value


def expand_kRSUnicode(value):
    pattern = re.compile(r"""
        (?P<radical>[1-9][0-9]{0,2})
        (?P<simplified>\'?)\.
        (?P<strokes>-?[0-9]{1,2})
    """, re.X)

    for i, v in enumerate(value):
        m = pattern.match(v).groupdict()
        value[i] = {
            "radical": int(m['radical']),
            "strokes": int(m['strokes']),
            "simplified": m['simplified'] == "'"
        }
    return value


def _expand_kRSGeneric(value):
    for i, v in enumerate(value):
        vals = v.split('.')
        value[i] = {
            "radical": int(vals[0]),
            "strokes": int(vals[1]),
        }
    return value


expand_kRSJapanese = _expand_kRSGeneric
expand_kRSKangXi = _expand_kRSGeneric
expand_kRSKanWa = _expand_kRSGeneric
expand_kRSKorean = _expand_kRSGeneric


def _expand_kIRG_GenericSource(value):
    v = value.split('-')
    return {
        "source": v[0],
        "location": v[1]
    }


expand_kIRG_GSource = _expand_kIRG_GenericSource
expand_kIRG_HSource = _expand_kIRG_GenericSource
expand_kIRG_JSource = _expand_kIRG_GenericSource
expand_kIRG_KPSource = _expand_kIRG_GenericSource
expand_kIRG_KSource = _expand_kIRG_GenericSource
expand_kIRG_MSource = _expand_kIRG_GenericSource
expand_kIRG_TSource = _expand_kIRG_GenericSource
expand_kIRG_USource = _expand_kIRG_GenericSource
expand_kIRG_VSource = _expand_kIRG_GenericSource


def expand_kGSR(value):
    pattern = re.compile(r"""
        (?P<set>[0-9]{4})
        (?P<letter>[a-vx-z])
        (?P<apostrophe>\')?
    """, re.X)

    for i, v in enumerate(value):
        m = pattern.match(v).groupdict()
        value[i] = {
            "set": int(m['set']),
            "letter": m['letter'],
            "apostrophe": m['apostrophe'] == "'"
        }
    return value


def expand_field(field, fvalue):
    """Return structured value of information in UNIHAN field.

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

    try:
        expansion_func = eval('expand_%s' % field)
        return expansion_func(fvalue)
    except NameError:
        pass

    return fvalue
