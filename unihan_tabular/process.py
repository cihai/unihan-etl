#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Build Unihan into tabular friendly format and export it."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import codecs
import fileinput
import glob
import json
import os
import shutil
import sys
import zipfile

from appdirs import AppDirs

from unihan_tabular._compat import urlretrieve, text_type, PY2
from unihan_tabular.util import _dl_progress, merge_dict, ucn_to_unicode

if PY2:
    import unicodecsv as csv
else:
    import csv

about = {}
about_file = os.path.join(os.path.dirname(__file__), '__about__.py')
with open(about_file) as fp:
    exec(fp.read(), about)

dirs = AppDirs(
    about['__package_name__'],  # appname
    about['__author__']    # app author
)


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


def in_fields(c, fields):
    """Return True if string is in the default fields."""
    return c in fields + INDEX_FIELDS


def get_fields(d):
    """Return list of fields from dict of {filename: ['field', 'field1']}."""
    return sorted({c for cs in d.values() for c in cs})


def filter_manifest(files):
    """Return filtered :attr:`~.UNIHAN_MANIFEST` from list of file names."""
    return {f: UNIHAN_MANIFEST[f] for f in files}


def files_exist(path, files):
    """Return True if all files exist in specified path."""
    return all(os.path.exists(os.path.join(path, f)) for f in files)


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


#: Directory to use for processing intermittent files.
WORK_DIR = os.path.join(dirs.user_cache_dir, 'downloads')
#: Default Unihan Files
UNIHAN_FILES = UNIHAN_MANIFEST.keys()
#: URI of Unihan.zip data.
UNIHAN_URL = 'http://www.unicode.org/Public/UNIDATA/Unihan.zip'
#: Filepath to output built CSV file to.
DESTINATION_DIR = dirs.user_data_dir
#: Filepath to download Zip file.
UNIHAN_ZIP_PATH = os.path.join(WORK_DIR, 'Unihan.zip')
#: Default Unihan fields
UNIHAN_FIELDS = get_fields(UNIHAN_MANIFEST)
#: Allowed export types
ALLOWED_EXPORT_TYPES = ['json', 'csv']
try:
    import yaml
    ALLOWED_EXPORT_TYPES += ['yaml']
except ImportError:
    pass

DEFAULT_OPTIONS = {
    'source': UNIHAN_URL,
    'destination': '%s/unihan.{ext}' % DESTINATION_DIR,
    'zip_path': UNIHAN_ZIP_PATH,
    'work_dir': WORK_DIR,
    'fields': INDEX_FIELDS + UNIHAN_FIELDS,
    'format': 'csv',
    'input_files': UNIHAN_FILES,
    'download': False
}


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
        "-z", "--zip-path", dest="zip_path",
        help="Path the zipfile is downloaded to. Default: %s" %
        UNIHAN_ZIP_PATH
    )
    parser.add_argument(
        "-d", "--destination", dest="destination",
        help="Output of .csv. Default: %s/unihan.{json,csv,yaml}" %
        DESTINATION_DIR
    )
    parser.add_argument(
        "-w", "--work-dir", dest="work_dir",
        help="Default: %s" % WORK_DIR
    )
    parser.add_argument(
        "-F", "--format", dest="format",
        choices=ALLOWED_EXPORT_TYPES,
        help="Default: %s" % DEFAULT_OPTIONS['format']
    )
    parser.add_argument(
        "-f", "--fields", dest="fields", nargs="*",
        help="Default: %s" % UNIHAN_FIELDS
    )
    parser.add_argument(
        "-i", "--input-files", dest="input_files", nargs='*',
        help="Default: %s, files inside zip to pull data from." % UNIHAN_FILES
    )
    return parser


def has_valid_zip(zip_path):
    """Return True if valid zip exists.

    :param zip_path: absolute path to zip
    :type zip_path: str
    :returns: True if valid zip exists at path
    :rtype: bool
    """

    if os.path.isfile(zip_path):
        if zipfile.is_zipfile(zip_path):
            print("Exists, is valid zip. %s" % zip_path)
            return True
        else:
            print("Not a valid zip. %s" % zip_path)
            return False
    else:
        print("File doesn't exist. %s" % zip_path)
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


def download(url, dest, urlretrieve_fn=urlretrieve, reporthook=None):
    """Download a file to a destination.

    :param url: URL to download from.
    :type url: str
    :param dest: file path where download is to be saved.
    :type dest: str
    :param urlretrieve_fn: function to download file
    :type urlretrieve_fn: function
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
            if os.path.isfile(url):
                shutil.copy(url, dest)
            elif reporthook:
                urlretrieve_fn(url, dest, reporthook)
            else:
                urlretrieve_fn(url, dest)

    return dest


def load_data(files):
    """Extract zip and process information into CSV's.

    :param files:
    :type files: list
    :rtype: str
    :returns: string of combined data from files
    """

    print('Loading data: %s.' % ', '.join(files))
    raw_data = fileinput.FileInput(
        files=files, openhook=fileinput.hook_encoded('utf-8')
    )
    print('Done loading data.')
    return raw_data


def extract_zip(zip_path, dest_dir):
    """Extract zip file. Return :class:`zipfile.ZipFile` instance.

    :param zip_path: filepath to extract.
    :type zip_path: str
    :param dest_dir: (optional) directory to extract to.
    :type dest_dir: str
    :returns: The extracted zip.
    :rtype: :class:`zipfile.ZipFile`

    """

    z = zipfile.ZipFile(zip_path)
    print('extract_zip dest dir: %s' % dest_dir)
    z.extractall(dest_dir)

    return z


def normalize(raw_data, fields):
    """Return normalized data from a UNIHAN data files.

    :param raw_data: combined text files from UNIHAN
    :type raw_data: str
    :param fields: list of columns to pull
    :type fields: list
    :return: list of unihan character information
    :rtype: list
    """
    print('Collecting field data...')
    items = dict()
    for idx, l in enumerate(raw_data):
        if not_junk(l):
            l = l.strip().split('\t')
            if in_fields(l[1], fields):
                item = dict(zip(['ucn', 'field', 'value'], l))
                char = ucn_to_unicode(item['ucn'])
                if char not in items:
                    items[char] = dict().fromkeys(fields)
                    items[char]['ucn'] = item['ucn']
                    items[char]['char'] = char
                items[char][item['field']] = text_type(item['value'])
        sys.stdout.write('\rProcessing line %i' % (idx))
        sys.stdout.flush()

    sys.stdout.write('\n')
    sys.stdout.flush()

    return [item for item in items.values()]


def listify(data, fields):
    """Convert tabularized data to a CSV-friendly list.

    :param data: List of dicts
    :type data: list
    :params fields: keys/columns, e.g. ['kDictionary']
    :type fields: list
    """
    list_data = [fields[:]]  # Add fields to first row
    list_data += [r.values() for r in [v for v in data]]  # Data
    return list_data


def export_csv(data, destination, fields):
    data = listify(data, fields)

    with open(destination, 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(data)
        print('Saved output to: %s' % destination)


def export_json(data, destination):
    with codecs.open(destination, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print('Saved output to: %s' % destination)


def export_yaml(data, destination):
    with codecs.open(destination, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, stream=f,
                       allow_unicode=True,
                       default_flow_style=False)
        print('Saved output to: %s' % destination)


def validate_options(options):
    if 'input_files' in options and 'fields' not in options:
        # Filter fields when only files specified.
        try:
            options['fields'] = get_fields(
                filter_manifest(options['input_files'])
            )
        except KeyError as e:
            raise KeyError('File {0} not found in file list.'.format(e))
    elif 'fields' in options and 'input_files' not in options:
        # Filter files when only field specified.
        options['input_files'] = get_files(options['fields'])
    elif 'fields' in options and 'input_files' in options:
        # Filter fields when only files specified.
        fields_in_files = get_fields(filter_manifest(options['input_files']))

        not_in_field = [
            h for h in options['fields'] if h not in fields_in_files
        ]
        if not_in_field:
            raise KeyError(
                'Field {0} not found in file list.'.format(
                    ', '.join(not_in_field)
                )
            )


class Packager(object):

    def __init__(self, options):
        """Download and generate a tabular release of
        `unihan <http://www.unicode.org/reports/tr38/>`_.

        :param options: options values to override defaults.
        :type options: dict

        """
        validate_options(options)

        self.options = merge_dict(DEFAULT_OPTIONS.copy(), options)

    def download(self, urlretrieve_fn=urlretrieve):
        """Download raw UNIHAN data if not exists.

        :param urlretrieve_fn: function to download file
        :type urlretrieve_fn: function
        """
        while not has_valid_zip(self.options['zip_path']):
            download(
                self.options['source'], self.options['zip_path'],
                urlretrieve_fn=urlretrieve_fn, reporthook=_dl_progress
            )

        if not files_exist(
            self.options['work_dir'], self.options['input_files']
        ):
            extract_zip(self.options['zip_path'], self.options['work_dir'])

    def export(self):
        """Extract zip and process information into CSV's."""

        fields = self.options['fields']
        for k in INDEX_FIELDS:
            if k not in fields:
                fields = [k] + fields

        files = [
            os.path.join(self.options['work_dir'], f)
            for f in self.options['input_files']
        ]

        # Replace {ext} with extension to use.
        self.options['destination'] = self.options['destination'].format(
            ext=self.options['format']
        )

        if not os.path.exists(os.path.dirname(self.options['destination'])):
            os.makedirs(self.options['destination'])

        data = load_data(
            files=files,
        )
        data = normalize(data, fields)
        if self.options['format'] == 'json':
            export_json(data, self.options['destination'])
        elif self.options['format'] == 'csv':
            export_csv(data, self.options['destination'], fields)
        elif self.options['format'] == 'yaml':
            export_yaml(data, self.options['destination'])
        elif self.options['format'] == 'python':
            return data
        else:
            print('Format %s does not exist' % self.options['format'])

    @classmethod
    def from_cli(cls, argv):
        """Create Packager instance from CLI :mod:`argparse` arguments.

        :param argv: Arguments passed in via CLI.
        :type argv: list
        :returns: builder
        :rtype: :class:`~.Packager`

        """
        parser = get_parser()

        args = parser.parse_args(argv)

        try:
            return cls({k: v for k, v in vars(args).items() if v})
        except Exception as e:
            sys.exit(e)


if __name__ == "__main__":
    p = Packager.from_cli(sys.argv[1:])
    p.download()
    p.export()
