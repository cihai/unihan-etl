#!/usr/bin/env python
# -*- coding: utf8 - *-
"""Build Unihan into datapackage-compatible format.

TODO: Parse datapackage.json's field and schema paramters.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import os
import sys
import zipfile
import glob
import hashlib
import fileinput
import argparse


__title__ = 'requests'
__description__ = 'Build Unihan into datapackage-compatible CSV.'
__version__ = '0.0.1'
__author__ = 'Tony Narlock'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Tony Narlock'


PY2 = sys.version_info[0] == 2

if PY2:
    unichr = unichr
    text_type = unicode
    string_types = (str, unicode)

    from urllib import urlretrieve
else:
    unichr = chr
    text_type = str
    string_types = (str,)

    from urllib.request import urlretrieve

#: Return False on newlines and C-style comments.
not_junk = lambda line: line[0] != '#' and line != '\n'

#: Return True if string is in the default headings.
in_headings = lambda c, columns: c in columns + default_columns
default_columns = ['ucn', 'char']
UNIHAN_URL = 'http://www.unicode.org/Public/UNIDATA/Unihan.zip'


def get_datapath(filename):

    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, 'data', filename
    ))

WORK_DIR = get_datapath('')
UNIHAN_DEST = get_datapath('data-built.csv')

#: Return list of headings from dict of {filename: ['heading', 'heading1']}.
get_headings = lambda d: sorted({c for cs in d.values() for c in cs})
default_columns = ['ucn', 'char']

#: Return filtered :dict:`~.UNIHAN_MANIFEST` by list of file names.
filter_manifest = lambda files: { f: UNIHAN_MANIFEST[f] for f in files }

UNIHAN_MANIFEST = {
    'Unihan_DictionaryIndices.txt': [
        'kCheungBauerIndex',
        'kCowles',
        'kDaeJaweon',
        'kFennIndex',
        'kGSR',
        'kHanYu',
        'kIRGDaeJaweon',
        'kIRGDaiKanwaZiten',
        'kIRGHanyuDaZidian',
        'kIRGKangXi',
        'kKangXi',
        'kKarlgren',
        'kLau',
        'kMatthews',
        'kMeyerWempe',
        'kMorohashi',
        'kNelson',
        'kSBGY',
    ],
    'Unihan_DictionaryLikeData.txt': [
        'kCangjie',
        'kCheungBauer',
        'kCihaiT',
        'kFenn',
        'kFourCornerCode',
        'kFrequency',
        'kGradeLevel',
        'kHDZRadBreak',
        'kHKGlyph',
        'kPhonetic',
        'kTotalStrokes',
    ],
    'Unihan_IRGSources.txt': [
        'kIICore',
        'kIRG_GSource',
        'kIRG_HSource',
        'kIRG_JSource',
        'kIRG_KPSource',
        'kIRG_KSource',
        'kIRG_MSource',
        'kIRG_TSource',
        'kIRG_USource',
        'kIRG_VSource',
    ],
    'Unihan_NumericValues.txt': [
        'kAccountingNumeric',
        'kOtherNumeric',
        'kPrimaryNumeric',
    ],
    'Unihan_OtherMappings.txt': [
        'kBigFive',
        'kCCCII',
        'kCNS1986',
        'kCNS1992',
        'kEACC',
        'kGB0',
        'kGB1',
        'kGB3',
        'kGB5',
        'kGB7',
        'kGB8',
        'kHKSCS',
        'kIBMJapan',
        'kJis0',
        'kJis1',
        'kJIS0213',
        'kKPS0',
        'kKPS1',
        'kKSC0',
        'kKSC1',
        'kMainlandTelegraph',
        'kPseudoGB1',
        'kTaiwanTelegraph',
        'kXerox',
    ],
    'Unihan_RadicalStrokeCounts.txt': [
        'kRSAdobe_Japan1_6',
        'kRSJapanese',
        'kRSKangXi',
        'kRSKanWa',
        'kRSKorean',
        'kRSUnicode',
    ],
    'Unihan_Readings.txt': [
        'kCantonese',
        'kDefinition',
        'kHangul',
        'kHanyuPinlu',
        'kHanyuPinyin',
        'kJapaneseKun',
        'kJapaneseOn',
        'kKorean',
        'kMandarin',
        'kTang',
        'kVietnamese',
        'kXHC1983',
    ],
    'Unihan_Variants.txt': [
        'kCompatibilityVariant',
        'kSemanticVariant',
        'kSimplifiedVariant',
        'kSpecializedSemanticVariant',
        'kTraditionalVariant',
        'kZVariant',
    ]

}


def ucn_to_unicode(ucn):
    """Convert a Unicode Universal Character Number (e.g. "U+4E00" or "4E00") to Python unicode (u'\\u4e00')"""
    if isinstance(ucn, string_types):
        ucn = ucn.strip("U+")
        if len(ucn) > int(4):
            char = b'\U' + format(int(ucn, 16), '08x').encode('latin1')
            char = char.decode('unicode_escape')
        else:
            char = unichr(int(ucn, 16))
    else:
        char = unichr(ucn)

    assert isinstance(char, text_type)

    return char


def save(url, filename, urlretrieve=urlretrieve, reporthook=None):
    """Separate download function for testability.

    :param url: URL to download
    :type url: str
    :param filename: destination to download to.
    :type filename: string
    :param urlretrieve: function to download file
    :type urlretrieve: function
    :param reporthook: callback for ``urlretrieve`` function progress.
    :type reporthook: function
    :returns: Result of ``urlretrieve`` function

    """

    if reporthook:
        return urlretrieve(url, filename, reporthook)
    else:
        return urlretrieve(url, filename)


def download(url, dest, urlretrieve=urlretrieve, reporthook=None):
    """Download a file to a destination.

    :param url: URL to download from.
    :type url: str
    :param destination: file path where download is to be saved.
    :type destination: str
    :param reporthook: Function to write progress bar to stdout buffer.
    :type reporthook: function
    :returns: destination where file downloaded to
    :rtype: str

    """

    datadir = os.path.dirname(dest)
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    no_unihan_files_exist = lambda: not glob.glob(
        os.path.join(datadir, 'Unihan*.txt')
    )

    not_downloaded = lambda: not os.path.exists(
        os.path.join(datadir, 'Unihan.zip')
    )

    if no_unihan_files_exist():
        if not_downloaded():
            print('Downloading Unihan.zip...')
            if reporthook:
                save(url, dest, urlretrieve, reporthook)
            else:
                save(url, dest, urlretrieve)

    return dest


def extract(zip_filepath):
    """Extract zip file. Return :class:`zipfile.ZipFile` instance.

    :param zip_filepath: file to extract.
    :type zip_filepath: string
    :returns: The extracted zip.
    :rtype: :class:`zipfile.ZipFile`

    """

    datadir = os.path.dirname(zip_filepath)
    try:
        z = zipfile.ZipFile(zip_filepath)
    except zipfile.BadZipfile as e:
        print('%s. Unihan.zip incomplete or corrupt. Redownloading...' % e)
        download()
        z = zipfile.ZipFile(zip_filepath)
    z.extractall(datadir)

    return z


def convert(csv_files, columns):
    """Return dict from Unihan CSV files.

    :param csv_files: file names in data dir
    :type csv_files: list
    :return: List of tuples for data loaded

    """

    data = fileinput.FileInput(files=csv_files, openhook=fileinput.hook_encoded('utf-8'))
    items = {}
    for l in data:
        if not_junk(l):
            l = l.strip().split('\t')
            if in_headings(l[1], columns):
                item = dict(zip(['ucn', 'field', 'value'], l))
                char = ucn_to_unicode(item['ucn'])
                if not char in items:
                    items[char] = dict.fromkeys(columns)
                    items[char]['ucn'] = item['ucn']
                items[char][item['field']] = item['value']
    return items


def build(
    source, destination, work_dir, headings, files
):

    print(source, destination, work_dir, headings, files)


def cli(argv):
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__
    )
    parser.add_argument("-s", "--source", action="append", dest="source",
                        help="Default: %s" % UNIHAN_URL)
    parser.add_argument("-d", "--destination", action="append", dest="destination",
                        help="Default: %s" % UNIHAN_DEST)
    parser.add_argument("-w", "--work-dir", action="append", dest="work_dir",
                        help="Default: %s" % WORK_DIR)
    parser.add_argument("-H", "--headings", action="append", dest="headings",
                        help="Default: %s" % UNIHAN_HEADINGS)
    parser.add_argument("-f", "--files", action="append", dest="files", nargs='*',
                        help="Default: %s" % UNIHAN_FILES)

    args = parser.parse_args(argv)

    source = args.source if args.source is not None else UNIHAN_URL
    destination = args.destination if args.destination is not None else UNIHAN_DEST
    work_dir = args.work_dir if args.work_dir is not None else WORK_DIR
    headings = args.headings if args.headings is not None else UNIHAN_HEADINGS
    files = args.files if args.files is not None else UNIHAN_FILES

    build(source, destination, work_dir, headings, files)

    parser.print_help()


def main():
    return cli(sys.argv[1:])

if __name__ == "__main__":
        sys.exit(main())
