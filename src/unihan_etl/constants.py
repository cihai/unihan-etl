"""Constants for unihan_etl."""
import importlib.util

from appdirs import AppDirs as BaseAppDirs

from unihan_etl.__about__ import (
    __author__,
    __package_name__,
)
from unihan_etl._internal.app_dirs import AppDirs
from unihan_etl.types import ColumnDataTuple
from unihan_etl.util import get_fields

#: Dictionary of tuples mapping locations of files to fields
UNIHAN_MANIFEST = {
    "Unihan_DictionaryIndices.txt": (
        "kCheungBauerIndex",
        "kCowles",
        "kDaeJaweon",
        "kFennIndex",
        "kGSR",
        "kHanYu",
        "kIRGDaeJaweon",
        "kIRGHanyuDaZidian",
        "kIRGKangXi",
        "kKangXi",
        "kKarlgren",
        "kLau",
        "kMatthews",
        "kMeyerWempe",
        "kMorohashi",
        "kNelson",
        "kSBGY",
        "kSMSZD2003Index",
    ),
    "Unihan_DictionaryLikeData.txt": (
        "kAlternateTotalStrokes",
        "kCangjie",
        "kCheungBauer",
        "kCihaiT",
        "kFenn",
        "kFourCornerCode",
        "kFrequency",
        "kGradeLevel",
        "kHDZRadBreak",
        "kHKGlyph",
        "kMojiJoho",
        "kPhonetic",
        "kStrange",
        "kTotalStrokes",
        "kUnihanCore2020",
    ),
    "Unihan_IRGSources.txt": (
        "kCompatibilityVariant",
        "kIICore",
        "kIRG_GSource",
        "kIRG_HSource",
        "kIRG_JSource",
        "kIRG_KPSource",
        "kIRG_KSource",
        "kIRG_MSource",
        "kIRG_SSource",
        "kIRG_TSource",
        "kIRG_USource",
        "kIRG_UKSource",
        "kIRG_VSource",
    ),
    "Unihan_NumericValues.txt": (
        "kAccountingNumeric",
        "kOtherNumeric",
        "kPrimaryNumeric",
        "kVietnameseNumeric",
        "kZhuangNumeric",
    ),
    "Unihan_OtherMappings.txt": (
        "kBigFive",
        "kCCCII",
        "kCNS1986",
        "kCNS1992",
        "kEACC",
        "kGB0",
        "kGB1",
        "kGB3",
        "kGB5",
        "kGB7",
        "kGB8",
        "kIBMJapan",
        "kJa",
        "kJinmeiyoKanji",
        "kJis0",
        "kJis1",
        "kJIS0213",
        "kJoyoKanji",
        "kKoreanEducationHanja",
        "kKoreanName",
        "kMainlandTelegraph",
        "kPseudoGB1",
        "kTaiwanTelegraph",
        "kTGH",
        "kXerox",
    ),
    "Unihan_RadicalStrokeCounts.txt": (
        "kRSAdobe_Japan1_6",
        "kRSUnicode",
    ),
    "Unihan_Readings.txt": (
        "kCantonese",
        "kDefinition",
        "kHangul",
        "kHanyuPinlu",
        "kHanyuPinyin",
        "kJapanese",
        "kJapaneseKun",
        "kJapaneseOn",
        "kKorean",
        "kMandarin",
        "kSMSZD2003Readings",
        "kTang",
        "kTGHZ2013",
        "kVietnamese",
        "kXHC1983",
    ),
    "Unihan_Variants.txt": (
        "kSemanticVariant",
        "kSimplifiedVariant",
        "kSpecializedSemanticVariant",
        "kSpoofingVariant",
        "kTraditionalVariant",
        "kZVariant",
    ),
}

#: FIELDS with multiple values via custom delimiters
CUSTOM_DELIMITED_FIELDS = (
    "kDefinition",
    "kDaeJaweon",
    "kHDZRadBreak",
    "kIRG_GSource",
    "kIRG_HSource",
    "kIRG_JSource",
    "kIRG_KPSource",
    "kIRG_KSource",
    "kIRG_MSource",
    "kIRG_SSource",
    "kIRG_TSource",
    "kIRG_USource",
    "kIRG_UKSource",
    "kIRG_VSource",
)

#: Fields with multiple values UNIHAN delimits by spaces -> dict
SPACE_DELIMITED_DICT_FIELDS = (
    "kAlternateTotalStrokes",
    "kHanYu",
    "kMandarin",
    "kTGHZ2013",
    "kSMSZD2003Index",
    "kSMSZD2003Readings",
    "kStrange",
    "kTotalStrokes",
    "kXHC1983",
)

#: Fields with multiple values UNIHAN delimits by spaces -> list
SPACE_DELIMITED_LIST_FIELDS = (
    "kAccountingNumeric",
    "kCantonese",
    "kCCCII",
    "kCheungBauer",
    "kCheungBauerIndex",
    "kCihaiT",
    "kCowles",
    "kFenn",
    "kFennIndex",
    "kFourCornerCode",
    "kGSR",
    "kHangul",
    "kHanyuPinlu",
    "kHanyuPinyin",
    "kHKGlyph",
    "kIBMJapan",
    "kIICore",
    "kIRGDaeJaweon",
    "kIRGHanyuDaZidian",
    "kIRGKangXi",
    "kJa",
    "kJapanese",
    "kJapaneseKun",
    "kJapaneseOn",
    "kJinmeiyoKanji",
    "kJis0",
    "kJIS0213",
    "kJis1",
    "kJoyoKanji",
    "kKangXi",
    "kKarlgren",
    "kKorean",
    "kKoreanEducationHanja",
    "kKoreanName",
    "kLua",
    "kMainlandTelegraph",
    "kMatthews",
    "kMeyerWempe",
    "kMorohashi",
    "kNelson",
    "kOtherNumeric",
    "kPhonetic",
    "kPrimaryNumeric",
    "kRSAdobe_Japan1_6",
    "kRSUnicode",
    "kSBGY",
    "kSemanticVariant",
    "kSimplifiedVariant",
    "kSpecializedSemanticVariant",
    "kSpoofingVariant",
    "kTaiwanTelegraph",
    "kTang",
    "kTGH",
    "kTraditionalVariant",
    "kVietnamese",
    "kVietnameseNumeric",
    "kXerox",
    "kZhuangNumeric",
    "kZVariant",
)

#: Any space delimited field regardless of expanded form
SPACE_DELIMITED_FIELDS = SPACE_DELIMITED_LIST_FIELDS + SPACE_DELIMITED_DICT_FIELDS

#: Default index fields for unihan csv's. You probably want these.
INDEX_FIELDS: ColumnDataTuple = ("ucn", "char")

app_dirs = AppDirs(_app_dirs=BaseAppDirs(__package_name__, __author__))


#: Directory to use for processing intermittent files.
WORK_DIR = app_dirs.user_cache_dir / "downloads"
#: Default Unihan Files
UNIHAN_FILES = list(UNIHAN_MANIFEST.keys())
#: URI of Unihan.zip data.
UNIHAN_URL = "http://www.unicode.org/Public/UNIDATA/Unihan.zip"
#: Filepath to output built CSV file to.
DESTINATION_DIR = app_dirs.user_data_dir
#: Filepath to download Zip file.
UNIHAN_ZIP_PATH = WORK_DIR / "Unihan.zip"
#: Default Unihan fields
UNIHAN_FIELDS: "ColumnDataTuple" = tuple(get_fields(UNIHAN_MANIFEST))
#: Allowed export types
ALLOWED_EXPORT_TYPES = ["json", "csv"]

if importlib.util.find_spec("yaml"):
    ALLOWED_EXPORT_TYPES += ["yaml"]
