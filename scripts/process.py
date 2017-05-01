#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Build Unihan into datapackage-compatible format."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import fileinput
import glob
import os
import sys
import zipfile

sys.path.insert(0, os.getcwd())  # NOQA we want to grab this:

from scripts._compat import urlretrieve
from scripts.unicodecsv import UnicodeWriter
from scripts.util import _dl_progress, merge_dict, ucn_to_unicode

about = {}
about_file = os.path.join(os.path.dirname(__file__), '..', '__about__.py')
with open(about_file) as fp:
    exec(fp.read(), about)

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

#: Default index fields for unihan csv's. You probably want these.
INDEX_FIELDS = ['ucn', 'char']


def not_junk(line):
    """Return False on newlines and C-style comments."""
    return line[0] != '#' and line != '\n'


def in_fields(c, columns):
    """Return True if string is in the default fields."""
    return c in columns + INDEX_FIELDS


def get_fields(d):
    """Return list of fields from dict of {filename: ['field', 'field1']}."""
    return sorted({c for cs in d.values() for c in cs})


def filter_manifest(files):
    """Return filtered :attr:`~.UNIHAN_MANIFEST` from list of file names."""
    return {f: UNIHAN_MANIFEST[f] for f in files}


#: Return path of a file inside data directory.
def get_datapath(filename):
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), os.pardir, 'data', filename
    ))


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


#: Directory to use for downloading files.
DATA_DIR = get_datapath('')
#: Directory to use for processing intermittent files.
WORK_DIR = get_datapath('downloads')
#: Default Unihan Files
UNIHAN_FILES = UNIHAN_MANIFEST.keys()
#: URI of Unihan.zip data.
UNIHAN_URL = 'http://www.unicode.org/Public/UNIDATA/Unihan.zip'
#: Filepath to output built CSV file to.
UNIHAN_DEST = get_datapath('unihan.csv')
#: Filepath to download Zip file.
UNIHAN_ZIP_FILEPATH = get_datapath('downloads/Unihan.zip')
#: Default Unihan fields
UNIHAN_FIELDS = get_fields(UNIHAN_MANIFEST)

default_options = {
    'source': UNIHAN_URL,
    'destination': UNIHAN_DEST,
    'zip_filepath': UNIHAN_ZIP_FILEPATH,
    'work_dir': WORK_DIR,
    'fields': INDEX_FIELDS + UNIHAN_FIELDS,
    'files': UNIHAN_FILES,
    'download': False
}


def save(url, filename, urlretrieve=urlretrieve, reporthook=None):
    """Separate download function for testability.

    :param url: URL to download
    :type url: str
    :param filename: destination to download to.
    :type filename: str
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

    def no_unihan_files_exist():
        return not glob.glob(
            os.path.join(datadir, 'Unihan*.txt')
        )

    def not_downloaded():
        return not os.path.exists(
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


def extract_zip(zip_filepath, work_dir=None):
    """Extract zip file. Return :class:`zipfile.ZipFile` instance.

    :param zip_filepath: filepath to extract.
    :type zip_filepath: str
    :param work_dir: (optional) directory to extract to. Defaults to
        :py:meth:`os.path.dirname` of ``zip_filepath``.
    :type work_dir: str
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

    import collections
    items = collections.OrderedDict()

    print('Processing files: %s.' % ', '.join(csv_files))
    data = fileinput.FileInput(
        files=csv_files, openhook=fileinput.hook_encoded('utf-8')
    )
    print('Done.')

    print('Collecting field data...')
    for idx, l in enumerate(data):
        if not_junk(l):
            l = l.strip().split('\t')
            if in_fields(l[1], columns):
                item = dict(zip(['ucn', 'field', 'value'], l))
                char = ucn_to_unicode(item['ucn'])
                if char not in items:
                    items[char] = collections.OrderedDict().fromkeys(columns)
                    items[char]['ucn'] = item['ucn']
                    items[char]['char'] = char
                items[char][item['field']] = item['value']
        sys.stdout.write('\rProcessing line %i.' % (idx))
        sys.stdout.flush()
    sys.stdout.write('\n')
    sys.stdout.flush()

    print('Done.')
    print('Converting to Simple Data Format.')
    datarows = [columns[:]] + [r.values() for r in [v for v in items.values()]]
    print('Done.')
    return datarows


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


def get_parser():
    """Return :py:class:`argparse.ArgumentParser` instance for CLI.

    :returns: argument parser for CLI use.
    :rtype: :py:class:`argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(
        prog=about['__title__'],
        description=about['__description__']
    )
    parser.add_argument(
        "-s", "--source", dest="source",
        help="URL or path of zipfile. Default: %s" % UNIHAN_URL)
    parser.add_argument(
        "-z", "--zip_filepath", dest="zip_filepath",
        help="Path the zipfile is downloaded to. Default: %s" %
        UNIHAN_ZIP_FILEPATH
    )
    parser.add_argument(
        "-d", "--destination", dest="destination",
        help="Output of .csv. Default: %s" % UNIHAN_DEST
    )
    parser.add_argument(
        "-w", "--work-dir", dest="work_dir",
        help="Default: %s" % WORK_DIR
    )
    parser.add_argument(
        "-F", "--fields", dest="fields", nargs="*",
        help="Default: %s" % UNIHAN_FIELDS
    )
    parser.add_argument(
        "-f", "--files", dest="files", nargs='*',
        help="Default: %s" % UNIHAN_FILES
    )
    return parser


class Builder(object):

    def __init__(self, options):
        """Download and generate a datapackage.json compatible release of
        `unihan <http://www.unicode.org/reports/tr38/>`_.

        :param options: options values to override defaults.
        :type options: dict

        """
        self.validate_options(options)

    def validate_options(self, options):

        if 'files' in options and 'fields' not in options:
            # Filter fields when only files specified.
            try:
                options['fields'] = get_fields(
                    filter_manifest(options['files'])
                )
            except KeyError as e:
                raise KeyError('File {0} not found in file list.'.format(e))
        elif 'fields' in options and 'files' not in options:
            # Filter files when only field specified.
            options['files'] = get_files(options['fields'])
        elif 'fields' in options and 'files' in options:
            # Filter fields when only files specified.
            fields_in_files = get_fields(filter_manifest(options['files']))

            not_in_field = [
                h for h in options['fields'] if h not in fields_in_files
            ]
            if not_in_field:
                raise KeyError(
                    'Field {0} not found in file list.'.format(
                        ', '.join(not_in_field)
                    )
                )

        self.options = merge_dict(default_options.copy(), options)

    def download(self):
        """Download raw UNIHAN data if not exists."""
        while not has_unihan_zip(self.options['zip_filepath']):
            download(self.options['source'], self['zip_filepath'],
                     reporthook=_dl_progress)

    def process(self):
        """Extract zip and process information into CSV's."""
        zip_file = extract_zip(self.options['zip_filepath'])

        if zip_has_files(self.options['files'], zip_file):
            print('All files in zip.')
            abs_paths = [
                os.path.join(self.options['work_dir'], f)
                for f in self.options['files']
            ]
            data = convert(abs_paths, self.options['fields'])

            with open(self.options['destination'], 'w+') as f:
                csvwriter = UnicodeWriter(f)
                csvwriter.writerows(data)
                print('Saved output to: %s.' % self.options['destination'])
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


if __name__ == "__main__":
    Builder.from_cli(sys.argv[1:])
