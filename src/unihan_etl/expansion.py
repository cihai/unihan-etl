"""Functions to uncompact details inside field values.

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
    """Expand kDefinition field."""
    return [c.strip() for c in value.split(";")]


kMandarinDict = t.TypedDict(
    "kMandarinDict",
    {"zh-Hans": str, "zh-Hant": str},
)


def expand_kMandarin(value: t.List[str]) -> kMandarinDict:
    """Expand kMandarin field."""
    cn = value[0]
    tw = value[0] if len(value) == 1 else value[1]
    return kMandarinDict({"zh-Hans": cn, "zh-Hant": tw})


kTotalStrokesDict = t.TypedDict(
    "kTotalStrokesDict",
    {"zh-Hans": int, "zh-Hant": int},
)


def expand_kTotalStrokes(value: t.List[str]) -> kTotalStrokesDict:
    """Expand kTotalStrokes field."""
    cn = value[0]
    tw = value[0] if len(value) == 1 else value[1]
    return kTotalStrokesDict({"zh-Hans": int(cn), "zh-Hant": int(tw)})


def expand_kUnihanCore2020(
    value: str,
) -> t.List[str]:
    """Expand kUnihanCore2020 field.

    Examples
    --------
    >>> expand_kUnihanCore2020('GHJ')
    ['G', 'H', 'J']
    """
    set_pattern = re.compile(
        r"""
        (?P<set>[GHJKMPT]{1})
    """,
        re.X,
    )
    items = set_pattern.split(value)
    sets = [s for s in items if s]
    return sets


class kLocationDict(t.TypedDict):
    """kLocation mapping."""

    volume: int
    page: int
    character: int
    virtual: int


def expand_kHanYu(value: t.List[str]) -> t.List[kLocationDict]:
    """Expand kHanYu field."""
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
    """Expand kIRGHanyuDaZidian field."""
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


class kTGHZ2013LocationDict(t.TypedDict):
    """kTGHZ2013 location mapping."""

    page: int
    position: int
    # 0 for a main entry and greater than 0 for a parenthesized or bracketed variant #
    # of the main entry
    entry_type: int


class kTGHZ2013Dict(t.TypedDict):
    """kTGHZ2013 mapping."""

    reading: str
    locations: t.Sequence[t.Union[str, kTGHZ2013LocationDict]]


def expand_kTGHZ2013(
    value: t.List[str],
) -> t.List[kTGHZ2013Dict]:
    """Expand kTGHZ2013 field.

    Examples
    --------
    >>> expand_kTGHZ2013(['097.110,097.120:fēng'])
    [{'reading': 'fēng', 'locations': [{'page': 97, 'position': 11, 'entry_type': 0},
    {'page': 97, 'position': 12, 'entry_type': 0}]}]

    >>> expand_kTGHZ2013(['482.140:zhòu'])  # doctest: +NORMALIZE_WHITESPACE
    [{'reading': 'zhòu', 'locations': [{'page': 482, 'position': 14, 'entry_type': 0}]}]
    """
    location_pattern = re.compile(
        r"""
        (?P<page>[\d]{3})\.
        (?P<position>[\d]{2})
        (?P<entry_type>[\d]{1})
    """,
        re.X,
    )

    expanded: t.List[kTGHZ2013Dict] = []

    for val in value:
        v = val.split(":")
        locations = v[0].split(",")
        reading = v[1]
        exploded_locations = []

        for loc in locations:
            m = location_pattern.match(loc)
            assert m is not None
            g = m.groupdict()
            assert g is not None

            exploded_locations.append(
                kTGHZ2013LocationDict(
                    page=int(g["page"]),
                    position=int(g["position"]),
                    entry_type=int(g["entry_type"]),
                )
            )
        expanded.append(
            kTGHZ2013Dict(
                reading=reading,
                locations=exploded_locations,
            )
        )
    return expanded


class kHanyuPinyinPreDict(t.TypedDict):
    """kHanyuPinyin predicate mapping."""

    locations: t.Sequence[t.Union[str, kLocationDict]]
    readings: t.List[str]


class kHanyuPinyinDict(t.TypedDict):
    """kHanyuPinyin mapping."""

    locations: kLocationDict
    readings: t.List[str]


def expand_kHanyuPinyin(
    value: t.List[str],
) -> t.List[kHanyuPinyinDict]:
    """Expand kHanyuPinyin field."""
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
    """kXHC1983 location mapping."""

    page: int
    character: int
    entry: t.Optional[int]
    substituted: bool


class kXHC1983Dict(t.TypedDict):
    """kXHC1983 mapping."""

    locations: kXHC1983LocationDict
    reading: str


class kXHC1983PreDict(t.TypedDict):
    """kXHC1983 predicate mapping."""

    locations: t.Union[t.List[str], kXHC1983LocationDict]
    reading: str


def expand_kXHC1983(
    value: t.List[str],
) -> t.List[kXHC1983Dict]:
    """Expand kXHC1983 field."""
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
    """kCheungBauer mapping."""

    radical: int
    strokes: int
    cangjie: t.Optional[str]
    readings: t.List[str]


def expand_kCheungBauer(
    value: t.List[str],
) -> t.List[kCheungBauerDict]:
    """Expand kCheungBauer field."""
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
    """Expand kRSAdobe_Japan1_6 field."""
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
    """kCihaiT mapping."""

    page: int
    row: int
    character: int


def expand_kCihaiT(value: t.List[str]) -> t.List[kCihaiTDict]:
    """Expand kCihaiT field."""
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
    """kIICore mapping."""

    priority: str
    sources: t.List[str]


def expand_kIICore(
    value: t.List[str],
) -> t.List[kIICoreDict]:
    """Expand kIICore field."""
    expanded: t.Sequence[t.Union[str, kIICoreDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = kIICoreDict(priority=v[0], sources=list(v[1:]))
    return expanded


class kDaeJaweonDict(t.TypedDict):
    """kDaehwan mapping."""

    page: int
    character: int
    virtual: int


def expand_kDaeJaweon(value: str) -> kDaeJaweonDict:
    """Expand kDaeJaweon field."""
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
    """Expand kIRGKangXi field."""
    expanded: t.Sequence[t.Union[str, kDaeJaweonDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = expand_kDaeJaweon(v)
    return expanded


def expand_kIRGDaeJaweon(value: t.List[str]) -> t.List[kDaeJaweonDict]:
    """Expand kIRGDaeJaweon field."""
    expanded: t.Sequence[t.Union[str, kDaeJaweonDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        expanded[i] = expand_kDaeJaweon(v)
    return expanded


class kFennDict(t.TypedDict):
    """kFenn mapping."""

    phonetic: str
    frequency: str


def expand_kFenn(value: t.List[str]) -> t.List[kFennDict]:
    """Expand kFenn field."""
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
    """kHanyuPinlu mapping."""

    phonetic: str
    frequency: int


def expand_kHanyuPinlu(value: t.List[str]) -> t.List[kHanyuPinluDict]:
    """Expand kHanyuPinlu field."""
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
    """Location mapping."""

    volume: int
    page: int
    character: int
    virtual: int


class kHDZRadBreakDict(t.TypedDict):
    """kHDZRadBreak mapping."""

    radical: str
    ucn: str
    location: LocationDict


def expand_kHDZRadBreak(value: str) -> kHDZRadBreakDict:
    """Expand kHDZRadBreak field."""
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
    """kSBGY mapping."""

    page: int
    character: int


def expand_kSBGY(value: t.List[str]) -> t.List[kSBGYDict]:
    """Expand kSBGY field."""
    expanded: t.Sequence[t.Union[str, kSBGYDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        vals = v.split(".")
        expanded[i] = kSBGYDict(page=int(vals[0]), character=int(vals[1]))
    return expanded


class kRSGenericDict(t.TypedDict):
    """kRSGeneric mapping."""

    radical: int
    strokes: int
    simplified: bool


def _expand_kRSGeneric(value: t.List[str]) -> t.List[kRSGenericDict]:
    """Expand kRSGeneric field.

    Examples
    --------
    >>> _expand_kRSGeneric(['5.10', "213''.0"])  # doctest: +NORMALIZE_WHITESPACE
    [{'radical': 5, 'strokes': 10, 'simplified': False},
    {'radical': 213, 'strokes': 0, 'simplified': False}]
    """
    pattern = re.compile(
        r"""
        (?P<radical>[1-9][0-9]{0,2})
        (?P<simplified>\'{0,2})\.
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
expand_kRSKangXi = _expand_kRSGeneric


class SourceLocationDict(t.TypedDict):
    """Source location mapping."""

    source: str
    location: t.Optional[str]


def _expand_kIRG_GenericSource(value: str) -> SourceLocationDict:
    """Expand kIRG_GenericSource field.

    Examples
    --------
    >>> _expand_kIRG_GenericSource('JMJ-056876')  # doctest: +NORMALIZE_WHITESPACE
    {'source': 'JMJ', 'location': '056876'}
    >>> _expand_kIRG_GenericSource('SAT-02570')  # doctest: +NORMALIZE_WHITESPACE
    {'source': 'SAT', 'location': '02570'}
    """
    v = value.split("-")
    return SourceLocationDict(source=v[0], location=v[1] if len(v) > 1 else None)


expand_kIRG_GSource = _expand_kIRG_GenericSource
expand_kIRG_HSource = _expand_kIRG_GenericSource
expand_kIRG_JSource = _expand_kIRG_GenericSource
expand_kIRG_KPSource = _expand_kIRG_GenericSource
expand_kIRG_KSource = _expand_kIRG_GenericSource
expand_kIRG_MSource = _expand_kIRG_GenericSource
expand_kIRG_SSource = _expand_kIRG_GenericSource
expand_kIRG_TSource = _expand_kIRG_GenericSource
expand_kIRG_USource = _expand_kIRG_GenericSource
expand_kIRG_UKSource = _expand_kIRG_GenericSource
expand_kIRG_VSource = _expand_kIRG_GenericSource


class kGSRDict(t.TypedDict):
    """kGSR mapping."""

    set: int
    letter: str
    apostrophe: bool


def expand_kGSR(value: t.List[str]) -> t.List[kGSRDict]:
    """Expand kGSR field."""
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
    """kCheungBauer mapping."""

    page: int
    character: int


def expand_kCheungBauerIndex(
    value: t.List[str],
) -> t.List[t.Union[str, kCheungBauerIndexDict]]:
    """Expand kCheungBauerIndex field."""
    expanded: t.Sequence[t.Union[str, kCheungBauerIndexDict]] = value.copy()
    assert isinstance(expanded, list)

    for i, v in enumerate(value):
        m = v.split(".")
        assert len(m) == 2
        expanded[i] = kCheungBauerIndexDict({"page": int(m[0]), "character": int(m[1])})
    return expanded


expand_kFennIndex = expand_kCheungBauerIndex


kStrangeLiteral = t.Literal[
    # Category A = [A]symmetric (exhibits a structure that is asymmetric)
    "A",
    # Category B = [B]opomofo (visually resembles a bopomofo character)
    "B",
    # Category C = [C]ursive (is cursive or includes one or more cursive components that
    # do not adhere to Han ideograph stroke conventions)
    "C",
    # Category F = [F]ully-reflective (is fully-reflective or includes components that
    # are fully-reflective, meaning that the mirrored and unmirrored components are
    # arranged side-by-side or stacked top-and-bottom)
    "F",
    # Category H = [H]angul Component (includes a hangul component)
    "H",
    # Category I = [I]ncomplete (appears to be an incomplete version of an existing or
    # possible ideograph, meaning that one or more components appear to be incomplete,
    # without regard to semantics)
    "I",
    # Category K = [K]atakana Component (includes one or more components that visually
    # resemble a katakana syllable)
    "K",
    # Category M = [M]irrored (is either mirrored or includes one or more components
    # that are mirrored)
    "M",
    # Category O = [O]dd Component (includes one or more components that are symbol-like
    # or are otherwise considered odd)
    "O",
    # Category R = [R]otated (is either rotated or includes one or more components that
    # are rotated)
    "R",
    # Category S = [S]troke-heavy (has 40 or more strokes)
    "S",
    # Category U = [U]nusual Arrangment/Structure (has an unusual structure or component
    # arrangement)
    "U",
]


class kStrangeDict(t.TypedDict):
    """kStrange mapping."""

    property_type: str
    characters: t.Sequence[str]


def expand_kStrange(
    value: t.List[str],
) -> t.List[kStrangeDict]:
    """Expand kStrange field.

    Examples
    --------
    >>> expand_kStrange(['B:U+310D', 'I:U+5DDB'])
    [{'property_type': 'B', 'characters': ['U+310D']},
    {'property_type': 'I', 'characters': ['U+5DDB']}]

    >>> expand_kStrange(['K:U+30A6:U+30C4:U+30DB'])  # doctest: +NORMALIZE_WHITESPACE
    [{'property_type': 'K', 'characters': ['U+30A6', 'U+30C4', 'U+30DB']}]

    >>> expand_kStrange(['U'])  # doctest: +NORMALIZE_WHITESPACE
    [{'property_type': 'U', 'characters': []}]
    """
    expanded: t.List[kStrangeDict] = []

    for val in value:
        if ":" in val:
            property_type, unexploded_chars = val.split(":", maxsplit=1)
            characters = unexploded_chars.split(":")
        else:
            property_type = val
            characters = []
        expanded.append(
            kStrangeDict(
                property_type=property_type,
                characters=characters,
            )
        )
    return expanded


def expand_field(field: str, fvalue: t.Union[str, t.List[str]]) -> t.Any:
    """Return structured value of information in UNIHAN field.

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
