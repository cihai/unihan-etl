#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Build Unihan into datapackage-compatible format."""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import os
import sys
import zipfile
import glob
import hashlib
import fileinput
import argparse
import csv
import codecs

from scripts.util import convert_to_attr_dict, merge_dict, _dl_progress, \
    ucn_to_unicode, ucnstring_to_python, ucnstring_to_unicode

from scripts._compat import urlretrieve, StringIO, PY2

from scripts.unicodecsv import UnicodeWriter


__title__ = 'cihaidata-unihan'
__description__ = 'Build Unihan into datapackage-compatible CSV.'
__version__ = '0.0.1'
__author__ = 'Tony Narlock'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Tony Narlock'


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

#: Return False on newlines and C-style comments.
not_junk = lambda line: line[0] != '#' and line != '\n'

#: Return True if string is in the default fields.
in_fields = lambda c, columns: c in columns + default_columns
default_columns = ['ucn', 'char']

#: Return list of fields from dict of {filename: ['field', 'field1']}.
get_fields = lambda d: sorted({c for cs in d.values() for c in cs})


def get_datapath(filename):

    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, 'data', filename
    ))

#: Return filtered :attr:`~.UNIHAN_MANIFEST` from list of file names.
filter_manifest = lambda files: {f: UNIHAN_MANIFEST[f] for f in files}


#: Return list of files from list of fields.
def get_files(fields):
    files = set()

    for field in fields:
        if field in UNIHAN_FIELDS:
            for file_, file_fields in UNIHAN_MANIFEST.items():
                if any(file_ for h in fields if h in file_fields):
                    files.add(file_)
        else:
            raise KeyError('Field {0} not found in file list.'.format(field))

    return list(files)

default_columns = ['ucn', 'char']

WORK_DIR = get_datapath('')
#: Default Unihan Files
UNIHAN_FILES = UNIHAN_MANIFEST.keys()
UNIHAN_URL = 'http://www.unicode.org/Public/UNIDATA/Unihan.zip'
UNIHAN_DEST = get_datapath('unihan.csv')
UNIHAN_ZIP_FILEPATH = get_datapath('Unihan.zip')
#: Default Unihan fields
UNIHAN_FIELDS = get_fields(UNIHAN_MANIFEST)

default_config = {
    'source': UNIHAN_URL,
    'destination': UNIHAN_DEST,
    'zip_filepath': UNIHAN_ZIP_FILEPATH,
    'work_dir': WORK_DIR,
    'fields': UNIHAN_FIELDS,
    'files': UNIHAN_FILES,
    'download': False
}


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
    :returns: destination where file downloaded to.
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
            print('%s to %s' % (url, dest))
            if reporthook:
                save(url, dest, urlretrieve, reporthook)
            else:
                save(url, dest, urlretrieve)

    return dest


def extract(zip_filepath, work_dir=None):
    """Extract zip file. Return :class:`zipfile.ZipFile` instance.

    :param zip_filepath: filepath to extract.
    :type zip_filepath: string
    :param work_dir: (optional) directory to extract to. Defaults to
        :py:meth:`os.path.dirname` of ``zip_filepath``.
    :type work_dir: string
    :returns: The extracted zip.
    :rtype: :class:`zipfile.ZipFile`

    """

    datadir = work_dir or os.path.dirname(zip_filepath)
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

    data = fileinput.FileInput(
        files=csv_files, openhook=fileinput.hook_encoded('utf-8')
    )
    items = {}
    for l in data:
        if not_junk(l):
            l = l.strip().split('\t')
            if in_fields(l[1], columns):
                item = dict(zip(['ucn', 'field', 'value'], l))
                char = ucn_to_unicode(item['ucn'])
                if not char in items:
                    items[char] = dict.fromkeys(columns)
                    items[char]['ucn'] = item['ucn']
                items[char][item['field']] = item['value']

    datarows = [columns[:]] + [r.values() for r in [v for v in items.values()]]
    return datarows


def get_parser():
    """Return :py:class:`argparse.ArgumentParser` instance for CLI.

    :returns: argument parser for CLI use.
    :rtype: :py:class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__
    )
    parser.add_argument("-s", "--source", dest="source",
                        help="URL or path of zipfile. Default: %s" % UNIHAN_URL)
    parser.add_argument("-z", "--zip_filepath", dest="zip_filepath",
                        help="Path the zipfile is downloaded to. Default: %s" % UNIHAN_ZIP_FILEPATH)
    parser.add_argument("-d", "--destination", dest="destination",
                        help="Output of .csv. Default: %s" % UNIHAN_DEST)
    parser.add_argument("-w", "--work-dir", dest="work_dir",
                        help="Default: %s" % WORK_DIR)
    parser.add_argument("-F", "--fields", dest="fields", nargs="*",
                        help="Default: %s" % UNIHAN_FIELDS)
    parser.add_argument("-f", "--files", dest="files", nargs='*',
                        help="Default: %s" % UNIHAN_FILES)
    return parser


class Builder(object):

    default_config = default_config

    def __init__(self, config):
        """Download and generate a datapackage.json compatible release of
        `unihan <http://www.unicode.org/reports/tr38/>`_.

        :param config: config values to override defaults.
        :type config: dict

        """

        if 'files' in config and 'fields' not in config:
            # Filter fields when only files specified.
            try:
                config['fields'] = get_fields(filter_manifest(config['files']))
            except KeyError as e:
                raise KeyError('File {0} not found in file list.'.format(e))
        elif 'fields' in config and 'files' not in config:
            # Filter files when only field specified.
            config['files'] = get_files(config['fields'])
        elif 'fields' in config and 'files' in config:
            # Filter fields when only files specified.
            fields_in_files = get_fields(filter_manifest(config['files']))

            not_in_field = [h for h in config['fields'] if h not in fields_in_files]
            if not_in_field:
                raise KeyError('Field {0} not found in file list.'.format(', '.join(not_in_field)))

        config = merge_dict(self.default_config, config)

        #: configuration dictionary. Available as attributes. ``.config.debug``
        self.config = convert_to_attr_dict(config)

        while not has_unihan_zip(self.config.zip_filepath):
            download(self.config.source, self.config.zip_filepath, reporthook=_dl_progress)

        zip_file = extract(self.config.zip_filepath)

        if zip_has_files(self.config.files, zip_file):
            print('All files in zip.')
            abs_paths = [os.path.join(self.config.work_dir, f) for f in self.config.files]
            data = convert(abs_paths, self.config.fields)

            with open(self.config.destination, 'w+') as f:
                csvwriter = UnicodeWriter(f)
                csvwriter.writerows(data)
        else:
            print('Missing files.')

    @classmethod
    def from_cli(cls, argv):
        """Create Builder instance from CLI :mod:`argparse` arguments.

        :param argv: Arguments passed in via CLI.
        :type argv: list
        :returns: builder
        :rtype: :class:`~.Builder`

        """
        parser = get_parser()

        args = parser.parse_args(argv)

        try:
            return cls({k: v for k, v in vars(args).items() if v})
        except Exception as e:
            sys.exit(e)


def has_unihan_zip(zip_filepath=None):
    """Return True if file has Unihan.zip and is a valid zip."""
    if not zip_filepath:
        zip_filepath = UNIHAN_ZIP_FILEPATH

    if os.path.isfile(zip_filepath):
        if zipfile.is_zipfile(zip_filepath):
            print("Exists, is valid zip. %s" % zip_filepath)
            return True
        else:
            print("Not a valid zip. %s" % zip_filepath)
            return False
    else:
        print("File doesn't exist. %s" % zip_filepath)
        return False


def zip_has_files(files, zip_file):
    """Return True if zip has the files inside.

    :param files: list of files inside zip
    :type files: list
    :param zip_file: zip file to look inside.
    :type zip_file: :py:class:`zipfile.ZipFile`
    :returns: True if files inside of `:py:meth:`zipfile.ZipFile.namelist()`.
    :rtype: bool

    """
    if set(files).issubset(set(zip_file.namelist())):
        return True
    else:
        return False


if __name__ == "__main__":
    Builder.from_cli(sys.argv[1:])
