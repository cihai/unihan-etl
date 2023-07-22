"""
Functions to uncompact details inside field values.

Notes
-----

:func:`re.compile` operations are inside of expand functions:

1. readability
2. module-level function bytecode is cached in python
3. the last used compiled regexes are cached
"""
import re
import typing as t

import zhon.hanzi
import zhon.pinyin

from unihan_etl.constants import SPACE_DELIMITED_FIELDS

#: diacritics from kHanyuPinlu
N_DIACRITICS = "ńňǹ"


def expand_kDefinition(value: str) -> t.List[str]:
    return [c.strip() for c in value.split(";")]


kMandarinDict = t.TypedDict(
    "kMandarinDict",
    {"zh-Hans": str, "zh-Hant": str},
)


def expand_kMandarin(value: t.List[str]) -> kMandarinDict:
    cn = value[0]
    tw = value[0] if len(value) == 1 else value[1]
    return kMandarinDict({"zh-Hans": cn, "zh-Hant": tw})


kTotalStrokesDict = t.TypedDict(
    "kTotalStrokesDict",
    {"zh-Hans": int, "zh-Hant": int},
)


def expand_kTotalStrokes(value: t.List[str]) -> kTotalStrokesDict:
    cn = value[0]
    tw = value[0] if len(value) == 1 else value[1]
    return kTotalStrokesDict({"zh-Hans": int(cn), "zh-Hant": int(tw)})


class kLocationDict(t.TypedDict):
    volume: int
    page: int
    character: int
    virtual: int


def expand_kHanYu(value: t.List[str]) -> t.List[kLocationDict]:
    pattern = re.compile(
        r"""
        (?P<volume>[1-8])
        (?P<page>[0-9]{4})\.
        (?P<character>[0-3][0-9])
        (?P<virtual>[0-3])
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kLocationDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None

        expanded[i] = kLocationDict(
            volume=int(m["volume"]),
            page=int(m["page"]),
            character=int(m["character"]),
            virtual=int(m["virtual"]),
        )
    return expanded


def expand_kIRGHanyuDaZidian(value: t.List[str]) -> t.List[kLocationDict]:
    pattern = re.compile(
        r"""
        (?P<volume>[1-8])
        (?P<page>[0-9]{4})\.
        (?P<character>[0-3][0-9])
        (?P<virtual>[01])
    """,
        re.X,
    )

    expanded: t.Sequence[t.Union[str, kLocationDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None

        expanded[i] = kLocationDict(
            volume=int(m["volume"]),
            page=int(m["page"]),
            character=int(m["character"]),
            virtual=int(m["virtual"]),
        )
    return expanded


class kHanyuPinyinPreDict(t.TypedDict):
    locations: t.Sequence[t.Union[str, kLocationDict]]
    readings: t.List[str]


class kHanyuPinyinDict(t.TypedDict):
    locations: kLocationDict
    readings: t.List[str]


def expand_kHanyuPinyin(
    value: t.List[str],
) -> t.List[kHanyuPinyinDict]:
    location_pattern = re.compile(
        r"""
        (?P<volume>[1-8])
        (?P<page>[0-9]{4})\.
        (?P<character>[0-3][0-9])
        (?P<virtual>[0-3])
    """,
        re.X,
    )

    expanded: t.Sequence[t.Union[str, kHanyuPinyinDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, val in enumerate(value):
        v = [s.split(",") for s in val.split(":")]
        expanded[i] = kHanyuPinyinPreDict(locations=v[0], readings=v[1])

        for n, loc in enumerate(expanded[i]["locations"]):
            m = location_pattern.match(loc)
            assert m is not None
            g = m.groupdict()
            assert g is not None

            expanded[i]["locations"][n] = kLocationDict(
                volume=int(g["volume"]),
                page=int(g["page"]),
                character=int(g["character"]),
                virtual=int(g["virtual"]),
            )
        expanded[i] = kHanyuPinyinDict(
            locations=expanded[i]["locations"], readings=expanded[i]["readings"]
        )
    return expanded


class kXHC1983LocationDict(t.TypedDict):
    page: int
    character: int
    entry: t.Optional[int]
    substituted: bool


class kXHC1983Dict(t.TypedDict):
    locations: kXHC1983LocationDict
    reading: str


class kXHC1983PreDict(t.TypedDict):
    locations: t.Union[t.List[str], kXHC1983LocationDict]
    reading: str


def expand_kXHC1983(
    value: t.List[str],
) -> t.List[kXHC1983Dict]:
    pattern = re.compile(
        r"""
        (?P<page>[0-9]{4})\.
        (?P<character>[0-9]{2})
        (?P<entry>[0-9]{1})
        (?P<substituted>\*?)
    """,
        re.X,
    )

    expanded: t.Sequence[t.Union[str, kXHC1983Dict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        vals = v.split(":")
        expanded[i] = kXHC1983PreDict(locations=vals[0].split(","), reading=vals[1])

        for n, loc in enumerate(expanded[i]["locations"]):
            m = pattern.match(loc)
            assert m is not None

            g = m.groupdict()
            assert g is not None

            expanded[i]["locations"][n] = kXHC1983LocationDict(
                page=int(g["page"]),
                character=int(g["character"]),
                entry=int(g["entry"]),
                substituted=g["substituted"] == "*",
            )
        expanded[i] = kXHC1983Dict(
            locations=expanded[i]["locations"], reading=expanded[i]["reading"]
        )
    return expanded


class kCheungBauerDict(t.TypedDict):
    radical: int
    strokes: int
    cangjie: t.Optional[str]
    readings: t.List[str]


def expand_kCheungBauer(
    value: t.List[str],
) -> t.List[kCheungBauerDict]:
    pattern = re.compile(
        r"""
        (?P<radical>[0-9]{3})\/(?P<strokes>[0-9]{2});
        (?P<cangjie>[A-Z]*);
        (?P<readings>[a-z1-6\[\]\/,]+)
    """,
        re.X,
    )

    expanded: t.Sequence[t.Union[str, kCheungBauerDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None

        expanded[i] = kCheungBauerDict(
            radical=int(m["radical"]),
            strokes=int(m["strokes"]),
            cangjie=m["cangjie"] or None,
            readings=m["readings"].split(","),
        )
    return expanded


kRSAdobe_Japan1_6Dict = t.TypedDict(
    "kRSAdobe_Japan1_6Dict",
    {"type": str, "cid": int, "radical": int, "strokes": int, "strokes-residue": int},
)


def expand_kRSAdobe_Japan1_6(value: t.List[str]) -> t.List[kRSAdobe_Japan1_6Dict]:
    pattern = re.compile(
        r"""
        (?P<type>[CV])\+
        (?P<cid>[0-9]{1,5})\+
        (?P<radical>[1-9][0-9]{0,2})\.
        (?P<strokes>[1-9][0-9]?)\.
        (?P<strokes_residue>[0-9]{1,2})
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kRSAdobe_Japan1_6Dict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None

        expanded[i] = kRSAdobe_Japan1_6Dict(
            {
                "type": g["type"],
                "cid": int(g["cid"]),
                "radical": int(g["radical"]),
                "strokes": int(g["strokes"]),
                "strokes-residue": int(g["strokes_residue"]),
            }
        )
    return expanded


class kCihaiTDict(t.TypedDict):
    page: int
    row: int
    character: int


def expand_kCihaiT(value: t.List[str]) -> t.List[kCihaiTDict]:
    pattern = re.compile(
        r"""
        (?P<page>[1-9][0-9]{0,3})\.
        (?P<row>[0-9]{1})
        (?P<character>[0-9]{2})
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kCihaiTDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None

        expanded[i] = kCihaiTDict(
            {
                "page": int(m["page"]),
                "row": int(m["row"]),
                "character": int(m["character"]),
            }
        )
    return expanded


class kIICoreDict(t.TypedDict):
    priority: str
    sources: t.List[str]


def expand_kIICore(
    value: t.List[str],
) -> t.List[kIICoreDict]:
    expanded: t.Sequence[t.Union[str, kIICoreDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = kIICoreDict(priority=v[0], sources=list(v[1:]))
    return expanded


class kDaeJaweonDict(t.TypedDict):
    page: int
    character: int
    virtual: int


def expand_kDaeJaweon(value: str) -> kDaeJaweonDict:
    pattern = re.compile(
        r"""
        (?P<page>[0-9]{4})\.
        (?P<character>[0-9]{2})
        (?P<virtual>[01])
    """,
        re.X,
    )
    m = pattern.match(value)
    assert m is not None

    g = m.groupdict()
    assert g is not None

    return kDaeJaweonDict(
        page=int(g["page"]),
        character=int(g["character"]),
        virtual=int(g["virtual"]),
    )


def expand_kIRGKangXi(value: t.List[str]) -> t.List[kDaeJaweonDict]:
    expanded: t.Sequence[t.Union[str, kDaeJaweonDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = expand_kDaeJaweon(v)
    return expanded


def expand_kIRGDaeJaweon(value: t.List[str]) -> t.List[kDaeJaweonDict]:
    expanded: t.Sequence[t.Union[str, kDaeJaweonDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = expand_kDaeJaweon(v)
    return expanded


class kFennDict(t.TypedDict):
    phonetic: str
    frequency: str


def expand_kFenn(value: t.List[str]) -> t.List[kFennDict]:
    pattern = re.compile(
        """
        (?P<phonetic>[0-9]+a?)
        (?P<frequency>[A-KP*])
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kFennDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None
        g = m.groupdict(v)
        assert g is not None

        expanded[i] = kFennDict(
            {"phonetic": g["phonetic"], "frequency": g["frequency"]}
        )
    return expanded


class kHanyuPinluDict(t.TypedDict):
    phonetic: str
    frequency: int


def expand_kHanyuPinlu(value: t.List[str]) -> t.List[kHanyuPinluDict]:
    pattern = re.compile(
        rf"""
        (?P<phonetic>[a-z({zhon.pinyin.lowercase}{N_DIACRITICS}]+)
        \((?P<frequency>[0-9]+)\)
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kHanyuPinluDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None
        g = m.groupdict()
        assert g is not None

        expanded[i] = kHanyuPinluDict(
            {"phonetic": g["phonetic"], "frequency": int(g["frequency"])}
        )
    return expanded


class LocationDict(t.TypedDict):
    volume: int
    page: int
    character: int
    virtual: int


class kHDZRadBreakDict(t.TypedDict):
    radical: str
    ucn: str
    location: LocationDict


def expand_kHDZRadBreak(value: str) -> kHDZRadBreakDict:
    rad, loc = value.split(":")

    loc_pattern = re.compile(
        r"""
        (?P<volume>[1-8])
        (?P<page>[0-9]{4})\.
        (?P<character>[0-3][0-9])
        (?P<virtual>[01])
    """,
        re.X,
    )

    loc_m = loc_pattern.match(loc)
    assert loc_m is not None
    loc_g = loc_m.groupdict()
    assert loc_g is not None

    location = LocationDict(
        volume=int(loc_g["volume"]),
        page=int(loc_g["page"]),
        character=int(loc_g["character"]),
        virtual=int(loc_g["virtual"]),
    )

    pattern = re.compile(
        rf"""
        (?P<radical>[{zhon.hanzi.radicals}]+)
        \[(?P<ucn>U\+2F[0-9A-D][0-9A-F])\]
    """,
        re.X,
    )
    m = pattern.match(rad)
    assert m is not None
    g = m.groupdict()
    assert g is not None

    return kHDZRadBreakDict(radical=g["radical"], ucn=g["ucn"], location=location)


class kSBGYDict(t.TypedDict):
    page: int
    character: int


def expand_kSBGY(value: t.List[str]) -> t.List[kSBGYDict]:
    expanded: t.Sequence[t.Union[str, kSBGYDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        vals = v.split(".")
        expanded[i] = kSBGYDict(page=int(vals[0]), character=int(vals[1]))
    return expanded


class kRSGenericDict(t.TypedDict):
    radical: int
    strokes: int
    simplified: bool


def _expand_kRSGeneric(value: t.List[str]) -> t.List[kRSGenericDict]:
    pattern = re.compile(
        r"""
        (?P<radical>[1-9][0-9]{0,2})
        (?P<simplified>\'?)\.
        (?P<strokes>-?[0-9]{1,2})
    """,
        re.X,
    )
    expanded: t.Sequence[t.Union[str, kRSGenericDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None
        g = m.groupdict()
        assert g is not None
        expanded[i] = kRSGenericDict(
            radical=int(g["radical"]),
            strokes=int(g["strokes"]),
            simplified=g["simplified"] == "'",
        )
    return expanded


expand_kRSUnicode = _expand_kRSGeneric
expand_kRSJapanese = _expand_kRSGeneric
expand_kRSKangXi = _expand_kRSGeneric
expand_kRSKanWa = _expand_kRSGeneric
expand_kRSKorean = _expand_kRSGeneric


class SourceLocationDict(t.TypedDict):
    source: str
    location: t.Optional[str]


def _expand_kIRG_GenericSource(value: str) -> SourceLocationDict:
    v = value.split("-")
    return SourceLocationDict(source=v[0], location=v[1] if len(v) > 1 else None)


expand_kIRG_GSource = _expand_kIRG_GenericSource
expand_kIRG_HSource = _expand_kIRG_GenericSource
expand_kIRG_JSource = _expand_kIRG_GenericSource
expand_kIRG_KPSource = _expand_kIRG_GenericSource
expand_kIRG_KSource = _expand_kIRG_GenericSource
expand_kIRG_MSource = _expand_kIRG_GenericSource
expand_kIRG_TSource = _expand_kIRG_GenericSource
expand_kIRG_USource = _expand_kIRG_GenericSource
expand_kIRG_VSource = _expand_kIRG_GenericSource


class kGSRDict(t.TypedDict):
    set: int
    letter: str
    apostrophe: bool


def expand_kGSR(value: t.List[str]) -> t.List[kGSRDict]:
    pattern = re.compile(
        r"""
        (?P<set>[0-9]{4})
        (?P<letter>[a-vx-z])
        (?P<apostrophe>\')?
    """,
        re.X,
    )

    expanded: t.Sequence[t.Union[str, kGSRDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = pattern.match(v)
        assert m is not None

        g = m.groupdict()
        assert g is not None
        expanded[i] = kGSRDict(
            {
                "set": int(g["set"]),
                "letter": g["letter"],
                "apostrophe": g["apostrophe"] == "'",
            }
        )
    return expanded


class kCheungBauerIndexDict(t.TypedDict):
    page: int
    character: int


def expand_kCheungBauerIndex(
    value: t.List[str],
) -> t.List[t.Union[str, kCheungBauerIndexDict]]:
    expanded: t.Sequence[t.Union[str, kCheungBauerIndexDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = v.split(".")
        assert len(m) == 2
        expanded[i] = kCheungBauerIndexDict({"page": int(m[0]), "character": int(m[1])})
    return expanded


expand_kFennIndex = expand_kCheungBauerIndex


def expand_field(field: str, fvalue: t.Union[str, t.List[str]]) -> t.Any:
    """
    Return structured value of information in UNIHAN field.

    Parameters
    ----------
    field : str
        field name
    fvalue : str
        value of field

    Returns
    -------
    list or dict :
        expanded field information per UNIHAN's documentation
    """
    if field in SPACE_DELIMITED_FIELDS and fvalue:
        assert isinstance(fvalue, str)
        fvalue = fvalue.split(" ")

    try:
        expansion_func = eval("expand_%s" % field)
        return expansion_func(fvalue)
    except NameError:
        pass

    return fvalue
