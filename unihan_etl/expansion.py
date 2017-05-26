# -*- coding: utf8 -*-
"""Functions to uncompact details inside field values."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import re

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
    """
    :note: Similar to kMandarin, except return values are int.
    """
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
    for i, v in enumerate(value):
        v = [c.strip() for c in v.split(':')]
        value[i] = {
            "locations": v[0],
            "readings": v[1]
        }
        for k, v in value[i].items():
            value[i][k] = v.split(',')
            if k == "locations":
                for ii, vvalue in enumerate(value[i][k]):
                    value[i][k][ii] = {
                        "volume": int(vvalue[0]),
                        "page": int(vvalue[1:5]),
                        "character": int(vvalue[6:8]),
                        "virtual": int(vvalue[8])
                    }
    return value


def expand_kXHC1983(value):
    for i, v in enumerate(value):
        vals = v.split(':')
        value[i] = {
            "locations": vals[0],
            "reading": vals[1],
        }
        for k, v in value[i].items():
            if k == "locations":
                value[i][k] = v.split(',')
                for ii, vvalue in enumerate(value[i][k]):
                    valz = vvalue.split('.')
                    substituted = valz[1][-1] == "*"
                    valz[1] = valz[1].replace("*", '')
                    value[i][k][ii] = {
                        "page": int(valz[0]),
                        "position": int(valz[1][0:2]),
                        "entry": int(valz[1][2]),
                        "substituted": substituted
                    }
    return value


def expand_kCheungBauer(value):
    for i, v in enumerate(value):
        v = [c.strip() for c in v.split(';')]
        value[i] = {
            "radical": int(v[0].split('/')[0]),
            "strokes": int(v[0].split('/')[1]),
            "cangjie": v[1] or None,
            "readings": v[2].split(',')
        }
    return value


def expand_kRSAdobe_Japan1_6(value):
    for i, v in enumerate(value):
        vals = v.split('+')
        value[i] = {
            "type": vals[0],
            "cid": int(vals[1]),
            "radical": int(vals[2].split('.')[0]),
            "strokes": int(vals[2].split('.')[1]),
            "strokes-residue": int(vals[2].split('.')[2])
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
    vals = value.split('.')
    value = {
        "page": int(vals[0]),
        "position": int(vals[1][0:2]),
        "virtual": int(vals[1][2]),
    }
    return value


def expand_kFenn(value):
    for i, v in enumerate(value):
        vre = re.split(r'(\d+)(\w+)', value[i])
        value[i] = {
            "phonetic": int(vre[1]),
            "frequency": vre[2]
        }
    return value


def expand_kHanyuPinlu(value):
    for i, v in enumerate(value):
        value[i] = {
            "phonetic": v[0:v.find("(")],
            "frequency": int(v[v.find("(")+1:v.find(")")])
        }
    return value


def expand_kHDZRadBreak(value):
    rad, loc = value.split(':')

    return {
        "radical": rad.split('[')[0],
        "ucn": rad.split('[')[1].replace(']', ''),
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
    for i, v in enumerate(value):
        vals = v.split('.')
        simp = vals[0][-1] == "'"
        value[i] = {
            "radical": int(vals[0].replace("'", '')),
            "strokes": int(vals[1]),
            "simplified": simp
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
