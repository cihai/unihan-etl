"""Test expansion of multi-value fields in UNIHAN."""

from __future__ import annotations

import typing as t

import pytest

from unihan_etl import constants, expansion

if t.TYPE_CHECKING:
    from typing import TypeAlias

ExpandedData: TypeAlias = list[dict[str, t.Any]]


def test_expands_spaces(unihan_quick_expanded_data: ExpandedData) -> None:
    """Test expansion expands spaces."""
    for item in unihan_quick_expanded_data:
        for field in item:
            if field in constants.SPACE_DELIMITED_LIST_FIELDS and item[field]:
                assert isinstance(item[field], list)


def test_expand_kCantonese(unihan_quick_expanded_data: ExpandedData) -> None:
    """Test expansion of kCantonese."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == "U+342B")
    if item["ucn"] == "U+342B":
        assert set(item["kCantonese"]) == {"gun3", "hung1", "zung1"}
    else:
        assert AssertionError("Missing U+342B kCantonese")


class ExpandFieldFixture(t.NamedTuple):
    """Fixture for test_expand."""

    test_id: str
    ucn: str
    field: str
    expected: list[str]


EXPAND_FIELD_FIXTURES: list[ExpandFieldFixture] = [
    ExpandFieldFixture(
        test_id="U+37AE-kJapaneseKun",
        ucn="U+37AE",
        field="kJapaneseKun",
        expected=["DERU", "DASU"],
    ),
    ExpandFieldFixture(
        test_id="U+37AE-kJapaneseOn",
        ucn="U+37AE",
        field="kJapaneseOn",
        expected=["SHUTSU", "SUI"],
    ),
    ExpandFieldFixture(
        test_id="U+37AE-kDefinition",
        ucn="U+37AE",
        field="kDefinition",
        expected=[
            "variant of 出 U+51FA, to go out, send out",
            "to stand",
            "to produce",
        ],
    ),
    ExpandFieldFixture(
        test_id="U+4FFE-kHangul",
        ucn="U+4FFE",
        field="kHangul",
        expected=["비"],
    ),
    ExpandFieldFixture(
        test_id="U+3427-kJapanese",
        ucn="U+3427",
        field="kJapanese",
        expected=["ダイ", "テイ", "ただ", "ついで", "やしき"],
    ),
    ExpandFieldFixture(
        test_id="U+91B1-kKorean",
        ucn="U+91B1",
        field="kKorean",
        expected=["PAL"],
    ),
    ExpandFieldFixture(
        test_id="U+91B1-kTang",
        ucn="U+91B1",
        field="kTang",
        expected=[r"pɑt"],  # NOQA: RUF001
    ),
]


@pytest.mark.parametrize(
    ExpandFieldFixture._fields,
    EXPAND_FIELD_FIXTURES,
    ids=[f.test_id for f in EXPAND_FIELD_FIXTURES],
)
def test_expand(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    field: str,
    expected: list[str],
) -> None:
    """Test expansion of kDefinition, kJapaneseKun, kJapaneseOn.

    kDefinition split on semicolons (";").
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert set(item[field]) == set(expected)


class ExpandKMandarinFixture(t.NamedTuple):
    """Fixture for test_expand_kMandarin."""

    test_id: str
    ucn: str
    expected: dict[str, str]


EXPAND_KMANDARIN_FIXTURES: list[ExpandKMandarinFixture] = [
    ExpandKMandarinFixture(
        test_id="U+346E",
        ucn="U+346E",
        expected={"zh-Hans": "hún", "zh-Hant": "hún"},  # U+346E	kMandarin	hún
    ),
    ExpandKMandarinFixture(
        test_id="U+4FFE",
        ucn="U+4FFE",
        expected={"zh-Hans": "bǐ", "zh-Hant": "bì"},  # U+4FFE	kMandarin	bǐ bì
    ),
]


@pytest.mark.parametrize(
    ExpandKMandarinFixture._fields,
    EXPAND_KMANDARIN_FIXTURES,
    ids=[f.test_id for f in EXPAND_KMANDARIN_FIXTURES],
)
def test_expand_kMandarin(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: dict[str, str],
) -> None:
    """Test expansion of KMandarin.

    From UNIHAN's documentation:

    The most customary pinyin reading for this character. When there are two
    values, then the first is preferred for zh-Hans (CN) and the second is
    preferred for zh-Hant (TW). When there is only one value, it is appropriate
    for both.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kMandarin"] == expected


class ExpandKTotalStrokesFixture(t.NamedTuple):
    """Fixture for test_expand_kTotalStrokes."""

    test_id: str
    ucn: str
    expected: dict[str, int]


EXPAND_KTOTAL_STROKES_FIXTURES: list[ExpandKTotalStrokesFixture] = [
    ExpandKTotalStrokesFixture(
        test_id="U+8303",
        ucn="U+8303",
        expected={"zh-Hans": 8, "zh-Hant": 9},  # U+8303	kTotalStrokes	8 9
    ),
    ExpandKTotalStrokesFixture(
        test_id="U+34D6",
        ucn="U+34D6",
        expected={"zh-Hans": 13, "zh-Hant": 13},  # U+34D6	kTotalStrokes	13
    ),
]


@pytest.mark.parametrize(
    ExpandKTotalStrokesFixture._fields,
    EXPAND_KTOTAL_STROKES_FIXTURES,
    ids=[f.test_id for f in EXPAND_KTOTAL_STROKES_FIXTURES],
)
def test_expand_kTotalStrokes(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: dict[str, int],
) -> None:
    """Test expansion of kTotalStrokes.

    From UNIHAN's documentation:

    The total number of strokes in the character (including the radical). When
    there are two values, then the first is preferred for zh-Hans (CN) and the
    second is preferred for zh-Hant (TW). When there is only one value, it is
    appropriate for both.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kTotalStrokes"] == expected


class ExpandKIRGHanyuDaZidianFixture(t.NamedTuple):
    """Fixture for test_expand_kIRGHanyuDaZidian."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KIRGHANYU_DA_ZIDIAN_FIXTURES: list[ExpandKIRGHanyuDaZidianFixture] = [
    # U+34AD      kIRGHanyuDaZidian       10273.120
    ExpandKIRGHanyuDaZidianFixture(
        test_id="U+34AD",
        ucn="U+34AD",
        expected=[{"volume": 1, "page": 273, "character": 12, "virtual": 0}],
    ),
    # U+34AF      kIRGHanyuDaZidian       10275.091
    ExpandKIRGHanyuDaZidianFixture(
        test_id="U+34AF",
        ucn="U+34AF",
        expected=[{"volume": 1, "page": 275, "character": 9, "virtual": 1}],
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGHanyuDaZidianFixture._fields,
    EXPAND_KIRGHANYU_DA_ZIDIAN_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGHANYU_DA_ZIDIAN_FIXTURES],
)
def test_expand_kIRGHanyuDaZidian(
    ucn: str,
    expected: ExpandedData,
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
) -> None:
    """Test expansion of kIRGHanyuDaZidian."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRGHanyuDaZidian"] == expected


class ExpandKHanyuPinyinFixture(t.NamedTuple):
    """Fixture for test_expand_kHanyuPinyin."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KHANYU_PINYIN_FIXTURES: list[ExpandKHanyuPinyinFixture] = [
    ExpandKHanyuPinyinFixture(
        test_id="U+5EFE",
        ucn="U+5EFE",
        expected=[
            {  # U+5EFE	kHanyuPinyin	10513.110,10514.010,10514.020:gǒng
                "locations": [
                    {"volume": 1, "page": 513, "character": 11, "virtual": 0},
                    {"volume": 1, "page": 514, "character": 1, "virtual": 0},
                    {"volume": 1, "page": 514, "character": 2, "virtual": 0},
                ],
                "readings": ["gǒng"],
            },
        ],
    ),
    ExpandKHanyuPinyinFixture(
        test_id="U+5364",
        ucn="U+5364",
        expected=[
            {  # U+5364	kHanyuPinyin	10093.130:xī,lǔ 74609.020:lǔ,xī
                "locations": [
                    {"volume": 1, "page": 93, "character": 13, "virtual": 0},
                ],
                "readings": ["xī", "lǔ"],
            },
            {
                "locations": [
                    {"volume": 7, "page": 4609, "character": 2, "virtual": 0},
                ],
                "readings": ["lǔ", "xī"],
            },
        ],
    ),
    ExpandKHanyuPinyinFixture(
        test_id="U+34D8",
        ucn="U+34D8",
        expected=[
            {  # U+34D8	kHanyuPinyin	10278.080,10278.090:sù
                "locations": [
                    {"volume": 1, "page": 278, "character": 8, "virtual": 0},
                    {"volume": 1, "page": 278, "character": 9, "virtual": 0},
                ],
                "readings": ["sù"],
            },
        ],
    ),
    ExpandKHanyuPinyinFixture(
        test_id="U+34CE",
        ucn="U+34CE",
        expected=[
            {  # U+34CE	kHanyuPinyin	10297.260:qīn,qìn,qǐn
                "locations": [
                    {"volume": 1, "page": 297, "character": 26, "virtual": 0},
                ],
                "readings": ["qīn", "qìn", "qǐn"],
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKHanyuPinyinFixture._fields,
    EXPAND_KHANYU_PINYIN_FIXTURES,
    ids=[f.test_id for f in EXPAND_KHANYU_PINYIN_FIXTURES],
)
def test_expand_kHanyuPinyin(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kHanyuPinyin.

    From UNIHAN's documentation:

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
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kHanyuPinyin"] == expected


class ExpandHanYuFixture(t.NamedTuple):
    """Fixture for test_expand_HanYu."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_HAN_YU_FIXTURES: list[ExpandHanYuFixture] = [
    ExpandHanYuFixture(
        test_id="U+9BF5",
        ucn="U+9BF5",
        expected=[
            {  # U+9BF5 kHanYu  74699.122
                "volume": 7,
                "page": 4699,
                "character": 12,
                "virtual": 2,
            },
        ],
    ),
    ExpandHanYuFixture(
        test_id="U+34B9",
        ucn="U+34B9",
        expected=[
            {  # U+34B9	kHanYu	10254.060 10254.100
                "volume": 1,
                "page": 254,
                "character": 6,
                "virtual": 0,
            },
            {"volume": 1, "page": 254, "character": 10, "virtual": 0},
        ],
    ),
    ExpandHanYuFixture(
        test_id="U+34AD",
        ucn="U+34AD",
        expected=[
            {  # U+34AD	kHanYu	10273.120
                "volume": 1,
                "page": 273,
                "character": 12,
                "virtual": 0,
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandHanYuFixture._fields,
    EXPAND_HAN_YU_FIXTURES,
    ids=[f.test_id for f in EXPAND_HAN_YU_FIXTURES],
)
def test_expand_HanYu(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of HanYu.

    From UNIHAN's documentation:

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
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kHanYu"] == expected


class ExpandKRSAdobeJapan16Fixture(t.NamedTuple):
    """Fixture for test_expand_kRSAdobe_Japan1_6."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KRSADOBE_JAPAN16_FIXTURES: list[ExpandKRSAdobeJapan16Fixture] = [
    # U+4E9D      kRSAdobe_Japan1_6       C+17245+7.2.6 C+17245+28.2.6
    ExpandKRSAdobeJapan16Fixture(
        test_id="U+4E9D",
        ucn="U+4E9D",
        expected=[
            {
                "type": "C",
                "cid": 17245,
                "radical": 7,
                "strokes": 2,
                "strokes-residue": 6,
            },
            {
                "type": "C",
                "cid": 17245,
                "radical": 28,
                "strokes": 2,
                "strokes-residue": 6,
            },
        ],
    ),
    # U+4E9E      kRSAdobe_Japan1_6       C+4108+7.2.6
    ExpandKRSAdobeJapan16Fixture(
        test_id="U+4E9E",
        ucn="U+4E9E",
        expected=[
            {
                "type": "C",
                "cid": 4108,
                "radical": 7,
                "strokes": 2,
                "strokes-residue": 6,
            },
        ],
    ),
    # U+4E30      kRSAdobe_Japan1_6       C+14301+2.1.3 V+15386+2.1.3
    ExpandKRSAdobeJapan16Fixture(
        test_id="U+4E30",
        ucn="U+4E30",
        expected=[
            {
                "type": "C",
                "cid": 14301,
                "radical": 2,
                "strokes": 1,
                "strokes-residue": 3,
            },
            {
                "type": "V",
                "cid": 15386,
                "radical": 2,
                "strokes": 1,
                "strokes-residue": 3,
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKRSAdobeJapan16Fixture._fields,
    EXPAND_KRSADOBE_JAPAN16_FIXTURES,
    ids=[f.test_id for f in EXPAND_KRSADOBE_JAPAN16_FIXTURES],
)
def test_expand_kRSAdobe_Japan1_6(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kRSAdobe_Japan1_6.

    From UNIHAN's documentation:

    The value consists of a number of space-separated entries. Each entry
    consists of three pieces of information separated by a plus sign:

    1) C or V. “C” indicates that the Unicode code point maps directly to the
    Adobe-Japan1-6 CID that appears after it, and “V” indicates that it is
    considered a variant form, and thus not directly encoded.

    2) The Adobe-Japan1-6 CID.

    3) Radical-stroke data for the indicated Adobe-Japan1-6 CID. The
    radical-stroke data consists of three pieces separated by periods: the
    KangXi radical (1-214), the number of strokes in the form the radical
    takes in the glyph, and the number of strokes in the residue. The standard
    Unicode radical-stroke form can be obtained by omitting the second value,
    and the total strokes in the glyph from adding the second and third
    values.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kRSAdobe_Japan1_6"] == expected


class ExpandKRSUnihanFixture(t.NamedTuple):
    """Fixture for test_expand_kRSUnihan."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KRSUNIHAN_FIXTURES: list[ExpandKRSUnihanFixture] = [
    # U+3491      kRSUnicode      9.13
    ExpandKRSUnihanFixture(
        test_id="U+3491",
        ucn="U+3491",
        expected=[
            {
                "radical": 9,
                "strokes": 13,
                "simplified": False,
            },
        ],
    ),
    # U+4336       kRSUnicode      120'.3
    ExpandKRSUnihanFixture(
        test_id="U+4336",
        ucn="U+4336",
        expected=[
            {
                "radical": 120,
                "strokes": 3,
                "simplified": expansion.kRSSimplifiedType.Chinese,
            },
        ],
    ),
    # U+2CC7B	kRSUnicode	182''.5 117.4
    ExpandKRSUnihanFixture(
        test_id="U+2CC7B",
        ucn="U+2CC7B",
        expected=[
            {
                "radical": 182,
                "strokes": 5,
                "simplified": expansion.kRSSimplifiedType.NonChinese,
            },
            {
                "radical": 117,
                "strokes": 4,
                "simplified": False,
            },
        ],
    ),
    # U+31E22	kRSUnicode	118.11 212'''.6
    ExpandKRSUnihanFixture(
        test_id="U+31E22",
        ucn="U+31E22",
        expected=[
            {
                "radical": 118,
                "strokes": 11,
                "simplified": False,
            },
            {
                "radical": 212,
                "strokes": 6,
                "simplified": expansion.kRSSimplifiedType.SecondNonChinese,
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKRSUnihanFixture._fields,
    EXPAND_KRSUNIHAN_FIXTURES,
    ids=[f.test_id for f in EXPAND_KRSUNIHAN_FIXTURES],
)
def test_expand_kRSUnihan(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kRSUnihan.

    From UNIHAN's documentation:

    The standard radical/stroke count for this character in the form
    “radical.additional strokes”. The radical is indicated by a number in the
    range (1..214) inclusive. An apostrophe (') after the radical indicates a
    simplified version of the given radical. The “additional strokes” value is
    the residual stroke-count, the count of all strokes remaining after
    eliminating all strokes associated with the radical.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kRSUnicode"] == expected


class ExpandKCheungBauerFixture(t.NamedTuple):
    """Fixture for test_expand_kCheungBauer."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KCHEUNG_BAUER_FIXTURES: list[ExpandKCheungBauerFixture] = [
    # U+34BC      kCheungBauer    055/08;TLBO;mang4
    ExpandKCheungBauerFixture(
        test_id="U+34BC",
        ucn="U+34BC",
        expected=[
            {"radical": 55, "strokes": 8, "cangjie": "TLBO", "readings": ["mang4"]}
        ],
    ),
    # U+356C  kCheungBauer    030/04;;gung1
    ExpandKCheungBauerFixture(
        test_id="U+356C",
        ucn="U+356C",
        expected=[
            {"radical": 30, "strokes": 4, "cangjie": None, "readings": ["gung1"]}
        ],
    ),
    # U+3598  kCheungBauer    030/07;RMMV;san2,seon2
    ExpandKCheungBauerFixture(
        test_id="U+3598",
        ucn="U+3598",
        expected=[
            {
                "radical": 30,
                "strokes": 7,
                "cangjie": "RMMV",
                "readings": ["san2", "seon2"],
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKCheungBauerFixture._fields,
    EXPAND_KCHEUNG_BAUER_FIXTURES,
    ids=[f.test_id for f in EXPAND_KCHEUNG_BAUER_FIXTURES],
)
def test_expand_kCheungBauer(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kCheungBauer.

    From UNIHAN's documentation:

    Each data value consists of three pieces, separated by semicolons:

    (1) the character`s radical-stroke index as a three-digit radical, slash,
    two-digit stroke count;
    (2) the character`s cangjie input code (if any); and
    (3) a comma-separated list of Cantonese readings using the jyutping
    romanization in alphabetical order.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kCheungBauer"] == expected


class ExpandKCihaiTFixture(t.NamedTuple):
    """Fixture for test_expand_kCihaiT."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KCIHAI_T_FIXTURES: list[ExpandKCihaiTFixture] = [
    # U+34D6      kCihaiT 170.105
    ExpandKCihaiTFixture(
        test_id="U+34D6",
        ucn="U+34D6",
        expected=[{"page": 170, "row": 1, "character": 5}],
    ),
]


@pytest.mark.parametrize(
    ExpandKCihaiTFixture._fields,
    EXPAND_KCIHAI_T_FIXTURES,
    ids=[f.test_id for f in EXPAND_KCIHAI_T_FIXTURES],
)
def test_expand_kCihaiT(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kCiHaiT.

    From UNIHAN's documentation:

    The position is indicated by a decimal number. The digits to the left of
    the decimal are the page number. The first digit after the decimal is the
    row on the page, and the remaining two digits after the decimal are the
    position on the row.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kCihaiT"] == expected


class ExpandKDaeJaweonFixture(t.NamedTuple):
    """Fixture for test_expand_kDaeJaweon."""

    test_id: str
    ucn: str
    expected: dict[str, int]


EXPAND_KDAE_JAWEON_FIXTURES: list[ExpandKDaeJaweonFixture] = [
    # U+9F7C  kDaeJaweon      2075.100
    ExpandKDaeJaweonFixture(
        test_id="U+9F7C",
        ucn="U+9F7C",
        expected={"page": 2075, "character": 10, "virtual": 0},
    ),
    # U+4E37  kDaeJaweon      0162.211
    ExpandKDaeJaweonFixture(
        test_id="U+4E37",
        ucn="U+4E37",
        expected={"page": 162, "character": 21, "virtual": 1},
    ),
]


@pytest.mark.parametrize(
    ExpandKDaeJaweonFixture._fields,
    EXPAND_KDAE_JAWEON_FIXTURES,
    ids=[f.test_id for f in EXPAND_KDAE_JAWEON_FIXTURES],
)
def test_expand_kDaeJaweon(
    unihan_quick_expanded_data: list[dict[str, t.Any]],
    test_id: str,
    ucn: str,
    expected: dict[str, int],
) -> None:
    """Test expansion kDaeJaweon.

    From UNIHAN's documentation:

    The position is in the form “page.position” with the final digit in the
    position being “0” for characters actually in the dictionary and “1” for
    characters not found in the dictionary and assigned a “virtual” position in
    the dictionary.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kDaeJaweon"] == expected


class ExpandKIICoreFixture(t.NamedTuple):
    """Fixture for test_expand_kIICore."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KIICORE_FIXTURES: list[ExpandKIICoreFixture] = [
    # U+48D3  kIICore CG
    ExpandKIICoreFixture(
        test_id="U+48D3",
        ucn="U+48D3",
        expected=[{"priority": "C", "sources": ["G"]}],
    ),
    # U+4E09  kIICore AGTJHKMP
    ExpandKIICoreFixture(
        test_id="U+4E09",
        ucn="U+4E09",
        expected=[{"priority": "A", "sources": ["G", "T", "J", "H", "K", "M", "P"]}],
    ),
    # U+4E0E  kIICore AGJ
    ExpandKIICoreFixture(
        test_id="U+4E0E",
        ucn="U+4E0E",
        expected=[{"priority": "A", "sources": ["G", "J"]}],
    ),
]


@pytest.mark.parametrize(
    ExpandKIICoreFixture._fields,
    EXPAND_KIICORE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIICORE_FIXTURES],
)
def test_expand_kIICore(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kIICore.

    From UNIHAN's documentation:

    Each value consists of a letter (A, B, or C), indicating priority value,
    and one or more letters (G, H, J, K, M, P, or T), indicating source. The
    source letters are the same as used for IRG sources, except that "P" is
    used instead of "KP".
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIICore"] == expected


class ExpandKIRGDaeJaweonFixture(t.NamedTuple):
    """Fixture for test_expand_kIRGDaeJaweon."""

    test_id: str
    ucn: str
    expected: list[dict[str, int]]


EXPAND_KIRGDAE_JAWEON_FIXTURES: list[ExpandKIRGDaeJaweonFixture] = [
    # U+4E07  kIRGDaeJaweon   0137.070
    ExpandKIRGDaeJaweonFixture(
        test_id="U+4E07",
        ucn="U+4E07",
        expected=[{"page": 137, "character": 7, "virtual": 0}],
    ),
    # U+4E37  kIRGDaeJaweon   0162.211
    ExpandKIRGDaeJaweonFixture(
        test_id="U+4E37",
        ucn="U+4E37",
        expected=[{"page": 162, "character": 21, "virtual": 1}],
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGDaeJaweonFixture._fields,
    EXPAND_KIRGDAE_JAWEON_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGDAE_JAWEON_FIXTURES],
)
def test_expand_kIRGDaeJaweon(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: list[dict[str, int]],
) -> None:
    """Test expansion of kIRGDaeJaweon."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRGDaeJaweon"] == expected


class ExpandKFennFixture(t.NamedTuple):
    """Fixture for test_expand_kFenn."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KFENN_FIXTURES: list[ExpandKFennFixture] = [
    # U+342C      kFenn   871P
    ExpandKFennFixture(
        test_id="U+342C",
        ucn="U+342C",
        expected=[{"phonetic": "871", "frequency": "P"}],
    ),
    # U+3431      kFenn   281K
    ExpandKFennFixture(
        test_id="U+3431",
        ucn="U+3431",
        expected=[{"phonetic": "281", "frequency": "K"}],
    ),
    # U+9918      kFenn   31A
    ExpandKFennFixture(
        test_id="U+9918",
        ucn="U+9918",
        expected=[{"phonetic": "31", "frequency": "A"}],
    ),
    # U+807D      kFenn   381aA
    ExpandKFennFixture(
        test_id="U+807D",
        ucn="U+807D",
        expected=[{"phonetic": "381a", "frequency": "A"}],
    ),
]


@pytest.mark.parametrize(
    ExpandKFennFixture._fields,
    EXPAND_KFENN_FIXTURES,
    ids=[f.test_id for f in EXPAND_KFENN_FIXTURES],
)
def test_expand_kFenn(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kFenn."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kFenn"] == expected


class ExpandKHanyuPinluFixture(t.NamedTuple):
    """Fixture for test_expand_kHanyuPinlu."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KHANYU_PINLU_FIXTURES: list[ExpandKHanyuPinluFixture] = [
    # U+4E0B      kHanyuPinlu     xià(6430) xia(249)
    ExpandKHanyuPinluFixture(
        test_id="U+4E0B",
        ucn="U+4E0B",
        expected=[
            {"phonetic": "xià", "frequency": 6430},
            {"phonetic": "xia", "frequency": 249},
        ],
    ),
    # U+4E09      kHanyuPinlu     sān(3030)
    ExpandKHanyuPinluFixture(
        test_id="U+4E09",
        ucn="U+4E09",
        expected=[{"phonetic": "sān", "frequency": 3030}],
    ),
    # U+55EF	kHanyuPinlu	ń(48) ň(48) ǹ(48) ńg(48) ňg(48) ǹg(48)
    ExpandKHanyuPinluFixture(
        test_id="U+55EF",
        ucn="U+55EF",
        expected=[
            {"phonetic": "ń", "frequency": 48},
            {"phonetic": "ň", "frequency": 48},
            {"phonetic": "ǹ", "frequency": 48},
            {"phonetic": "ńg", "frequency": 48},
            {"phonetic": "ňg", "frequency": 48},
            {"phonetic": "ǹg", "frequency": 48},
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKHanyuPinluFixture._fields,
    EXPAND_KHANYU_PINLU_FIXTURES,
    ids=[f.test_id for f in EXPAND_KHANYU_PINLU_FIXTURES],
)
def test_expand_kHanyuPinlu(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kHanyuPinlu.

    From UNIHAN's documentation:

    Immediately following the pronunciation, a numeric string appears in
    parentheses: e.g. in “ā(392)” the numeric string “392” indicates the sum
    total of the frequencies of the pronunciations of the character as given in
    HYPLCD.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kHanyuPinlu"] == expected


class ExpandKHDZRadBreakFixture(t.NamedTuple):
    """Fixture for test_expand_kHDZRadBreak."""

    test_id: str
    ucn: str
    expected: dict[str, t.Any]


EXPAND_KHDZRAD_BREAK_FIXTURES: list[ExpandKHDZRadBreakFixture] = [
    # U+4E00  kHDZRadBreak    ⼀[U+2F00]:10001.010
    ExpandKHDZRadBreakFixture(
        test_id="U+4E00",
        ucn="U+4E00",
        expected={
            "radical": "⼀",
            "ucn": "U+2F00",
            "location": {"volume": 1, "page": 1, "character": 1, "virtual": False},
        },
    ),
    # U+4E59  kHDZRadBreak    ⼄[U+2F04]:10047.040
    ExpandKHDZRadBreakFixture(
        test_id="U+4E59",
        ucn="U+4E59",
        expected={
            "radical": "⼄",
            "ucn": "U+2F04",
            "location": {"volume": 1, "page": 47, "character": 4, "virtual": False},
        },
    ),
]


@pytest.mark.parametrize(
    ExpandKHDZRadBreakFixture._fields,
    EXPAND_KHDZRAD_BREAK_FIXTURES,
    ids=[f.test_id for f in EXPAND_KHDZRAD_BREAK_FIXTURES],
)
def test_expand_kHDZRadBreak(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: dict[str, t.Any],
) -> None:
    """Test expansion of kHDZRadBreak.

    From UNIHAN's documentation:

    Hanyu Da Zidian has a radical break beginning at this character`s position.
    The field consists of the radical (with its Unicode code point), a colon,
    and then the Hanyu Da Zidian position as in the kHanyu field.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kHDZRadBreak"] == expected


class ExpandKSBGYFixture(t.NamedTuple):
    """Fixture for test_expand_kSBGY."""

    test_id: str
    ucn: str
    expected: ExpandedData


EXPAND_KSBGY_FIXTURES: list[ExpandKSBGYFixture] = [
    # U+349D      kSBGY   479.12 495.09
    ExpandKSBGYFixture(
        test_id="U+349D",
        ucn="U+349D",
        expected=[{"page": 479, "character": 12}, {"page": 495, "character": 9}],
    ),
    # U+349F      kSBGY   296.38
    ExpandKSBGYFixture(
        test_id="U+349F",
        ucn="U+349F",
        expected=[{"page": 296, "character": 38}],
    ),
]


@pytest.mark.parametrize(
    ExpandKSBGYFixture._fields,
    EXPAND_KSBGY_FIXTURES,
    ids=[f.test_id for f in EXPAND_KSBGY_FIXTURES],
)
def test_expand_kSBGY(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: ExpandedData,
) -> None:
    """Test expansion of kSBGY.

    From UNIHAN's documentation:

    The 25334 character references are given in the form “ABC.XY”, in which:
    "ABC” is the zero-padded page number [004..546]; “XY” is the zero-padded
    number of the character on the page [01..73]. For example, 364.38
    indicates the 38th character on Page 364 (i.e. 澍). Where a given Unicode
    Scalar Value (USV) has more than one reference, these are space-delimited.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kSBGY"] == expected


class ExpandKXHC1983Fixture(t.NamedTuple):
    """Fixture for test_expand_kXHC1983."""

    test_id: str
    ucn: str
    fieldval: str
    expected: list[dict[str, list[dict[str, int | bool]] | str]]


EXPAND_KXHC1983_FIXTURES: list[ExpandKXHC1983Fixture] = [
    # U+91B1  kXHC1983        0295.011:fā 0884.081:pō
    ExpandKXHC1983Fixture(
        test_id="U+91B1",
        ucn="U+91B1",
        fieldval="0295.011:fā 0884.081:pō",
        expected=[
            {
                "locations": [
                    {"page": 295, "character": 1, "entry": 1, "substituted": False},
                ],
                "reading": "fā",
            },
            {
                "locations": [
                    {"page": 884, "character": 8, "entry": 1, "substituted": False},
                ],
                "reading": "pō",
            },
        ],
    ),
    # U+379E  kXHC1983        1092.070*,1092.071:sóng
    ExpandKXHC1983Fixture(
        test_id="U+379E",
        ucn="U+379E",
        fieldval="1092.070*,1092.071:sóng",
        expected=[
            {
                "locations": [
                    {"page": 1092, "character": 7, "entry": 0, "substituted": True},
                    {
                        "page": 1092,
                        "character": 7,
                        "entry": 1,
                        "substituted": False,
                    },
                ],
                "reading": "sóng",
            },
        ],
    ),
    # U+5750  kXHC1983        1551.040,1552.011:zuò
    ExpandKXHC1983Fixture(
        test_id="U+5750",
        ucn="U+5750",
        fieldval="1551.040,1552.011:zuò",
        expected=[
            {
                "locations": [
                    {
                        "page": 1551,
                        "character": 4,
                        "entry": 0,
                        "substituted": False,
                    },
                    {
                        "page": 1552,
                        "character": 1,
                        "entry": 1,
                        "substituted": False,
                    },
                ],
                "reading": "zuò",
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKXHC1983Fixture._fields,
    EXPAND_KXHC1983_FIXTURES,
    ids=[f.test_id for f in EXPAND_KXHC1983_FIXTURES],
)
def test_expand_kXHC1983(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: list[dict[str, list[dict[str, int | bool]] | str]],
) -> None:
    r"""Tests for expansion of kXHC1983.

    From UNIHAN's documentation:

    Each pīnyīn reading is preceded by the character`s location(s) in the
    dictionary, separated from the reading by “:” (colon); multiple locations
    for a given reading are separated by “,” (comma); multiple “location:
    reading” values are separated by “ ” (space). Each location reference is of
    the form /[0-9]{4}\.[0-9]{3}\*?/ . The number preceding the period is the
    page number, zero-padded to four digits. The first two digits of the number
    following the period are the entry`s position on the page, zero-padded. The
    third digit is 0 for a main entry and greater than 0 for a parenthesized
    variant of the main entry. A trailing “*” (asterisk) on the location
    indicates an encoded variant substituted for an unencoded character (see
    below).

    As of the present writing (Unicode 5.1), the XHC source data contains 204
    unencoded characters (198 of which were represented by PUA or CJK
    Compatibility [or in one case, by non-CJK, see below] characters), for the
    most part simplified variants. Each of these 198 characters in the source
    is replaced by one or more encoded variants (references in all 204 cases
    are marked with a trailing “*”; see above). Many of these unencoded forms
    are already in the pipeline for future encoding, and future revisions of
    this data will eliminate trailing asterisks from mappings.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kXHC1983"] == expected

    assert expansion.expand_field("kXHC1983", fieldval) == expected


class ExpandKTGHZ2013Fixture(t.NamedTuple):
    """Fixture for test_expand_kTGHZ2013."""

    test_id: str
    ucn: str
    fieldval: str
    expected: list[dict[str, list[dict[str, int | bool]] | str]]


EXPAND_KTGHZ2013_FIXTURES: list[ExpandKTGHZ2013Fixture] = [
    # U+3447	kTGHZ2013	482.140:zhòu
    ExpandKTGHZ2013Fixture(
        test_id="U+3447",
        ucn="U+3447",
        fieldval="482.140:zhòu",
        expected=[
            {
                "locations": [
                    {
                        "page": 482,
                        "position": 14,
                        "entry_type": 0,
                    },
                ],
                "reading": "zhòu",
            },
        ],
    ),
    # U+4E0A	kTGHZ2013	326.050:shǎng 326.090:shàng
    ExpandKTGHZ2013Fixture(
        test_id="U+4E0A",
        ucn="U+4E0A",
        fieldval="326.050:shǎng 326.090:shàng",
        expected=[
            {
                "locations": [
                    {
                        "page": 326,
                        "position": 5,
                        "entry_type": 0,
                    },
                ],
                "reading": "shǎng",
            },
            {
                "locations": [
                    {
                        "page": 326,
                        "position": 9,
                        "entry_type": 0,
                    },
                ],
                "reading": "shàng",
            },
        ],
    ),
    # U+4E30	kTGHZ2013	097.110,097.120:fēng
    ExpandKTGHZ2013Fixture(
        test_id="U+4E30",
        ucn="U+4E30",
        fieldval="097.110,097.120:fēng",
        expected=[
            {
                "locations": [
                    {
                        "page": 97,
                        "position": 11,
                        "entry_type": 0,
                    },
                    {
                        "page": 97,
                        "position": 12,
                        "entry_type": 0,
                    },
                ],
                "reading": "fēng",
            },
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKTGHZ2013Fixture._fields,
    EXPAND_KTGHZ2013_FIXTURES,
    ids=[f.test_id for f in EXPAND_KTGHZ2013_FIXTURES],
)
def test_expand_kTGHZ2013(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: list[dict[str, list[dict[str, int | bool]] | str]],
) -> None:
    r"""Tests for expansion of kTGHZ2013.

    From UNIHAN's documentation:

    Each pīnyīn reading is preceded by the ideograph's location(s) in the dictionary,
    separated from the reading by a colon. Multiple locations for a given reading are
    separated by commas. Multiple “location: reading” values are separated by a space.
    Each location reference is of the form /[0-9]{3}\.[0-9]{3}/. The number preceding
    the period is the page number, zero-padded to three digits. The first two digits of
    the number following the period are the entry's position on the page, zero-padded.
    The third digit is 0 for a main entry and greater than 0 for a parenthesized or
    bracketed variant of the main entry.
    """
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)

    assert expansion.expand_field("kTGHZ2013", fieldval) == expected

    assert item["kTGHZ2013"] == expected


class ExpandKIRGGSourceFixture(t.NamedTuple):
    """Fixture for test_expand_kIRG_GSource."""

    test_id: str
    ucn: str
    fieldval: str
    expected: dict[str, str | None]


EXPAND_KIRGGSOURCE_FIXTURES: list[ExpandKIRGGSourceFixture] = [
    # U+348C      kIRG_GSource    GKX-0118.03
    ExpandKIRGGSourceFixture(
        test_id="U+348C",
        ucn="U+348C",
        fieldval="GKX-0118.03",
        expected={"source": "GKX", "location": "0118.03"},
    ),
    # U+2A660  kIRG_GSource    G4K
    ExpandKIRGGSourceFixture(
        test_id="U+2A660",
        ucn="U+2A660",
        fieldval="G4K",
        expected={"source": "G4K", "location": None},
    ),
    # U+348D      kIRG_GSource    G5-3272
    ExpandKIRGGSourceFixture(
        test_id="U+348D",
        ucn="U+348D",
        fieldval="G5-3272",
        expected={"source": "G5", "location": "3272"},
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGGSourceFixture._fields,
    EXPAND_KIRGGSOURCE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGGSOURCE_FIXTURES],
)
def test_expand_kIRG_GSource(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: dict[str, str | None],
) -> None:
    """Tests for expansion kIRG_GSource."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRG_GSource"] == expected

    assert expansion.expand_field("kIRG_GSource", fieldval) == expected


class ExpandKIRGHSourceFixture(t.NamedTuple):
    """Fixture for test_expand_kIRG_HSource."""

    test_id: str
    ucn: str
    fieldval: str
    expected: dict[str, str]


EXPAND_KIRGHSOURCE_FIXTURES: list[ExpandKIRGHSourceFixture] = [
    # U+347E      kIRG_HSource    H-8F59
    ExpandKIRGHSourceFixture(
        test_id="U+347E",
        ucn="U+347E",
        fieldval="H-8F59",
        expected={"source": "H", "location": "8F59"},
    ),
    # U+4E00      kIRG_HSource    HB1-A440
    ExpandKIRGHSourceFixture(
        test_id="U+4E00",
        ucn="U+4E00",
        fieldval="HB1-A440",
        expected={"source": "HB1", "location": "A440"},
    ),
    # U+4E07      kIRG_HSource    HB2-C945
    ExpandKIRGHSourceFixture(
        test_id="U+4E07",
        ucn="U+4E07",
        fieldval="HB2-C945",
        expected={"source": "HB2", "location": "C945"},
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGHSourceFixture._fields,
    EXPAND_KIRGHSOURCE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGHSOURCE_FIXTURES],
)
def test_expand_kIRG_HSource(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: dict[str, str],
) -> None:
    """Tests for expansion kIRG_HSource."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRG_HSource"] == expected

    assert expansion.expand_field("kIRG_HSource", fieldval) == expected


class ExpandKIRGJSourceFixture(t.NamedTuple):
    """Fixture for test_expand_kIRG_JSource."""

    test_id: str
    ucn: str
    fieldval: str
    expected: dict[str, str]


EXPAND_KIRGJSOURCE_FIXTURES: list[ExpandKIRGJSourceFixture] = [
    # U+3400	kIRG_JSource	JA-2121
    ExpandKIRGJSourceFixture(
        test_id="U+3400",
        ucn="U+3400",
        fieldval="JA-2121",
        expected={"source": "JA", "location": "2121"},
    ),
    # U+3402	kIRG_JSource	JA3-2E23
    ExpandKIRGJSourceFixture(
        test_id="U+3402",
        ucn="U+3402",
        fieldval="JA3-2E23",
        expected={"source": "JA3", "location": "2E23"},
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGJSourceFixture._fields,
    EXPAND_KIRGJSOURCE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGJSOURCE_FIXTURES],
)
def test_expand_kIRG_JSource(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: dict[str, str],
) -> None:
    """Tests for expansion kIRG_JSource."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRG_JSource"] == expected

    assert expansion.expand_field("kIRG_JSource", fieldval) == expected


class ExpandKIRGKPSourceFixture(t.NamedTuple):
    """Fixture for test_expand_kIRG_KPSource."""

    test_id: str
    field: str
    ucn: str
    fieldval: str
    expected: dict[str, str]


EXPAND_KIRGKPSOURCE_FIXTURES: list[ExpandKIRGKPSourceFixture] = [
    # U+3ED0  kIRG_KPSource   KP0-EAB2
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_KPSource-U+3ED0",
        field="kIRG_KPSource",
        ucn="U+3ED0",
        fieldval="KP0-EAB2",
        expected={"source": "KP0", "location": "EAB2"},
    ),
    # U+340C  kIRG_KPSource   KP1-3451
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_KPSource-U+340C",
        field="kIRG_KPSource",
        ucn="U+340C",
        fieldval="KP1-3451",
        expected={"source": "KP1", "location": "3451"},
    ),
    # U+4E06  kIRG_KSource    K2-2121
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_KSource-U+4E06",
        field="kIRG_KSource",
        ucn="U+4E06",
        fieldval="K2-2121",
        expected={"source": "K2", "location": "2121"},
    ),
    # U+3401  kIRG_KSource    K3-2121
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_KSource-U+3401",
        field="kIRG_KSource",
        ucn="U+3401",
        fieldval="K3-2121",
        expected={"source": "K3", "location": "2121"},
    ),
    # U+21290	kIRG_MSource	MAC-00077
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_MSource-U+21290",
        field="kIRG_MSource",
        ucn="U+21290",
        fieldval="MAC-00077",
        expected={"source": "MAC", "location": "00077"},
    ),
    # U+3400  kIRG_TSource    T6-222C
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_TSource-U+3400",
        field="kIRG_TSource",
        ucn="U+3400",
        fieldval="T6-222C",
        expected={"source": "T6", "location": "222C"},
    ),
    # U+3401  kIRG_TSource    T4-2224
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_TSource-U+3401",
        field="kIRG_TSource",
        ucn="U+3401",
        fieldval="T4-2224",
        expected={"source": "T4", "location": "2224"},
    ),
    # U+2CEBC	kIRG_SSource	SAT-04823
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_SSource-U+2CEBC",
        field="kIRG_SSource",
        ucn="U+2CEBC",
        fieldval="SAT-04823",
        expected={"source": "SAT", "location": "04823"},
    ),
    # U+22016 kIRG_USource    UTC-00069
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_USource-U+22016",
        field="kIRG_USource",
        ucn="U+22016",
        fieldval="UTC-00069",
        expected={"source": "UTC", "location": "00069"},
    ),
    # U+2DE4A	kIRG_UKSource	UK-02896
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_UKSource-U+2DE4A",
        field="kIRG_UKSource",
        ucn="U+2DE4A",
        fieldval="UK-02896",
        expected={"source": "UK", "location": "02896"},
    ),
    # U+346B  kIRG_VSource    V0-3034
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_VSource-U+346B",
        field="kIRG_VSource",
        ucn="U+346B",
        fieldval="V0-3034",
        expected={"source": "V0", "location": "3034"},
    ),
    # U+340C  kIRG_VSource    V2-8874
    ExpandKIRGKPSourceFixture(
        test_id="kIRG_VSource-U+340C",
        field="kIRG_VSource",
        ucn="U+340C",
        fieldval="V2-8874",
        expected={"source": "V2", "location": "8874"},
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGKPSourceFixture._fields,
    EXPAND_KIRGKPSOURCE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGKPSOURCE_FIXTURES],
)
def test_expand_kIRG_KPSource(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    field: str,
    ucn: str,
    fieldval: str,
    expected: dict[str, str],
) -> None:
    """Tests for expansion of kIRG_KPSource."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item[field] == expected

    assert expansion.expand_field(field, fieldval) == expected


class ExpandKGSRFixture(t.NamedTuple):
    """Fixture for test_expand_kGSR."""

    test_id: str
    ucn: str
    fieldval: str
    expected: ExpandedData


EXPAND_KGSR_FIXTURES: list[ExpandKGSRFixture] = [
    # U+340C  kGSR    0004f
    ExpandKGSRFixture(
        test_id="U+340C",
        ucn="U+340C",
        fieldval="0004f",
        expected=[{"set": 4, "letter": "f", "apostrophe": False}],
    ),
    # U+371D	kGSR	0651k'
    ExpandKGSRFixture(
        test_id="U+371D",
        ucn="U+371D",
        fieldval="0651k'",
        expected=[{"set": 651, "letter": "k", "apostrophe": True}],
    ),
    # U+9AE2  kGSR    0004e' 0850s
    ExpandKGSRFixture(
        test_id="U+9AE2",
        ucn="U+9AE2",
        fieldval="0004e' 0850s",
        expected=[
            {"set": 4, "letter": "e", "apostrophe": True},
            {"set": 850, "letter": "s", "apostrophe": False},
        ],
    ),
]


@pytest.mark.parametrize(
    ExpandKGSRFixture._fields,
    EXPAND_KGSR_FIXTURES,
    ids=[f.test_id for f in EXPAND_KGSR_FIXTURES],
)
def test_expand_kGSR(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: ExpandedData,
) -> None:
    """Tests for expansion of kGSR."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kGSR"] == expected

    assert expansion.expand_field("kGSR", fieldval) == expected


class ExpandKCheungBauerIndexFixture(t.NamedTuple):
    """Fixture for test_expand_kCheungBauerIndex."""

    test_id: str
    ucn: str
    fieldval: str
    expected: ExpandedData


EXPAND_KCHEUNG_BAUER_INDEX_FIXTURES: list[ExpandKCheungBauerIndexFixture] = [
    # U+34BC  kCheungBauerIndex       402.06
    ExpandKCheungBauerIndexFixture(
        test_id="U+34BC",
        ucn="U+34BC",
        fieldval="402.06",
        expected=[{"page": 402, "character": 6}],
    ),
    # U+3578  kCheungBauerIndex       351.02 351.03
    ExpandKCheungBauerIndexFixture(
        test_id="U+3578",
        ucn="U+3578",
        fieldval="351.02 351.03",
        expected=[{"page": 351, "character": 2}, {"page": 351, "character": 3}],
    ),
]


@pytest.mark.parametrize(
    ExpandKCheungBauerIndexFixture._fields,
    EXPAND_KCHEUNG_BAUER_INDEX_FIXTURES,
    ids=[f.test_id for f in EXPAND_KCHEUNG_BAUER_INDEX_FIXTURES],
)
def test_expand_kCheungBauerIndex(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: ExpandedData,
) -> None:
    """Tests for expansion of kCheungBauerIndex."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kCheungBauerIndex"] == expected

    assert expansion.expand_field("kCheungBauerIndex", fieldval) == expected


class ExpandKFennIndexFixture(t.NamedTuple):
    """Fixture for test_expand_kFennIndex."""

    test_id: str
    ucn: str
    fieldval: str
    expected: ExpandedData


EXPAND_KFENN_INDEX_FIXTURES: list[ExpandKFennIndexFixture] = [
    # U+348B      kFennIndex      480.05
    ExpandKFennIndexFixture(
        test_id="U+348B",
        ucn="U+348B",
        fieldval="480.05",
        expected=[{"page": 480, "character": 5}],
    ),
    # U+349A      kFennIndex      602.04
    ExpandKFennIndexFixture(
        test_id="U+349A",
        ucn="U+349A",
        fieldval="602.04",
        expected=[{"page": 602, "character": 4}],
    ),
]


@pytest.mark.parametrize(
    ExpandKFennIndexFixture._fields,
    EXPAND_KFENN_INDEX_FIXTURES,
    ids=[f.test_id for f in EXPAND_KFENN_INDEX_FIXTURES],
)
def test_expand_kFennIndex(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: ExpandedData,
) -> None:
    """Tests for expansion of kFennIndex."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kFennIndex"] == expected

    assert expansion.expand_field("kFennIndex", fieldval) == expected


class ExpandKIRGKangXiFixture(t.NamedTuple):
    """Fixture for test_expand_kIRGKangXi."""

    test_id: str
    ucn: str
    fieldval: str
    expected: ExpandedData


EXPAND_KIRGKANG_XI_FIXTURES: list[ExpandKIRGKangXiFixture] = [
    # U+34AD      kIRGKangXi      0125.190
    ExpandKIRGKangXiFixture(
        test_id="U+34AD",
        ucn="U+34AD",
        fieldval="0125.190",
        expected=[{"page": 125, "character": 19, "virtual": 0}],
    ),
    # U+34AE      kIRGKangXi      0125.201
    ExpandKIRGKangXiFixture(
        test_id="U+34AE",
        ucn="U+34AE",
        fieldval="0125.201",
        expected=[{"page": 125, "character": 20, "virtual": 1}],
    ),
]


@pytest.mark.parametrize(
    ExpandKIRGKangXiFixture._fields,
    EXPAND_KIRGKANG_XI_FIXTURES,
    ids=[f.test_id for f in EXPAND_KIRGKANG_XI_FIXTURES],
)
def test_expand_kIRGKangXi(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: ExpandedData,
) -> None:
    """Tests for expansion of kIRGKangXi."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kIRGKangXi"] == expected

    assert expansion.expand_field("kIRGKangXi", fieldval) == expected


class ExpandKCCCIIFixture(t.NamedTuple):
    """Fixture for test_expand_kCCCII."""

    test_id: str
    ucn: str
    fieldval: str
    expected: list[str]


EXPAND_KCCCII_FIXTURES: list[ExpandKCCCIIFixture] = [
    # U+4E00	kCCCII	213021
    ExpandKCCCIIFixture(
        test_id="U+4E00",
        ucn="U+4E00",
        fieldval="213021",
        expected=["213021"],
    ),
    # U+4E0D	kCCCII	21302A
    ExpandKCCCIIFixture(
        test_id="U+4E0D",
        ucn="U+4E0D",
        fieldval="21302A",
        expected=["21302A"],
    ),
]


@pytest.mark.parametrize(
    ExpandKCCCIIFixture._fields,
    EXPAND_KCCCII_FIXTURES,
    ids=[f.test_id for f in EXPAND_KCCCII_FIXTURES],
)
def test_expand_kCCCII(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    fieldval: str,
    expected: list[str],
) -> None:
    """Tests for expansion of kCCCII."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kCCCII"] == expected

    assert expansion.expand_field("kCCCII", fieldval) == expected


class ExpandKFanqieFixture(t.NamedTuple):
    """Fixture for test_expand_kFanqie."""

    test_id: str
    ucn: str
    expected: list[dict[str, str]]


EXPAND_KFANQIE_FIXTURES: list[ExpandKFanqieFixture] = [
    ExpandKFanqieFixture(
        test_id="U+3A4B",
        ucn="U+3A4B",
        expected=[
            {"initial": "蘇", "final": "彫"},
            {"initial": "先", "final": "鳥"},
            {"initial": "蘇", "final": "弔"},
            {"initial": "所", "final": "六"},
            {"initial": "息", "final": "逐"},
        ],
    ),
    ExpandKFanqieFixture(
        test_id="U+3A53",
        ucn="U+3A53",
        expected=[{"initial": "許", "final": "委"}],
    ),
]


@pytest.mark.parametrize(
    ExpandKFanqieFixture._fields,
    EXPAND_KFANQIE_FIXTURES,
    ids=[f.test_id for f in EXPAND_KFANQIE_FIXTURES],
)
def test_expand_kFanqie(
    unihan_quick_expanded_data: ExpandedData,
    test_id: str,
    ucn: str,
    expected: list[dict[str, str]],
) -> None:
    """Test expansion of kFanqie."""
    item = next(i for i in unihan_quick_expanded_data if i["ucn"] == ucn)
    assert item["kFanqie"] == expected
