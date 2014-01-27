# -*- coding: utf-8 -*-
"""Tests for unihan.

cihaidata_unihan.testsuite.unihan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use datapackage.json format.

1. insert dict/struct of { 'unihanFileName': ['colName', 'colName'] }
return cols, records

    Idea: Create a special iter class for it.
    Idea 2: Function, return cols, struct above

What a data set should provide.

1. Download the code.
2. Extract it (if necessary).
3. Extract the code


"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import os
import sys
import tempfile
import logging
import unittest
import zipfile
import shutil

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


from scripts import process

from scripts.process import UNIHAN_URL, UNIHAN_DEST, WORK_DIR, UNIHAN_HEADINGS, \
    UNIHAN_FILES, default_config, Builder
from scripts.util import merge_dict


log = logging.getLogger(__name__)


def add_to_path(path):
    """Adds an entry to sys.path if it's not already there.  This does
    not append it but moves it to the front so that we can be sure it
    is loaded.
    """
    if not os.path.isdir(path):
        raise RuntimeError('Tried to add nonexisting path')

    def _samefile(x, y):
        if x == y:
            return True
        try:
            return os.path.samefile(x, y)
        except (IOError, OSError, AttributeError):
            # Windows has no samefile
            return False
    sys.path[:] = [x for x in sys.path if not _samefile(path, x)]
    sys.path.insert(0, path)


def setup_path():
    script_path = os.path.join(
        os.path.dirname(__file__), os.pardir, 'scripts'
    )
    add_to_path(script_path)


def get_datapath(filename):

    return os.path.join(
        os.path.dirname(__file__), 'fixtures', filename
    )


class TestCase(unittest.TestCase):
    pass


class UnihanHelper(TestCase):

    config = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'test_config.yml'
    ))

    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.mkdtemp()
        cls.zip_filename = 'zipfile.zip'
        cls.tempzip_filepath = os.path.join(cls.tempdir, cls.zip_filename)
        zf = zipfile.ZipFile(cls.tempzip_filepath, 'a')
        zf.writestr("d.txt", "DDDDDDDDDD")
        zf.close()

        cls.zf = zf

        super(UnihanHelper, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)
        super(UnihanHelper, cls).tearDownClass()


class UnihanScriptsTestCase(UnihanHelper):

    def test_in_headings(self):
        columns = ['hey', 'kDefinition', 'kWhat']
        result = process.in_headings('kDefinition', columns)

        self.assertTrue(result)

    def test_save(self):

        src_filepath = self.tempzip_filepath

        tempdir = tempfile.mkdtemp()

        dest_filepath = os.path.join(tempdir, self.zip_filename)
        process.save(src_filepath, dest_filepath, shutil.copy)

        result = os.path.exists(dest_filepath)

        shutil.rmtree(tempdir)

        self.assertTrue(result)

    def test_download(self):

        src_filepath = self.tempzip_filepath

        tempdir = self.tempdir
        dest_filepath = os.path.join(tempdir, 'data', self.zip_filename)

        process.download(src_filepath, dest_filepath, shutil.copy)

        result = os.path.dirname(os.path.join(dest_filepath, 'data'))
        self.assertTrue(
            result,
            msg="Creates data directory if doesn't exist."
        )

    def test_extract(self):

        zf = process.extract(self.tempzip_filepath)

        self.assertEqual(len(zf.infolist()), 1)
        self.assertEqual(zf.infolist()[0].file_size, 10)
        self.assertEqual(zf.infolist()[0].filename, "d.txt")

    def test_convert(self):
        csv_files = [
            get_datapath('Unihan_DictionaryLikeData.txt'),
            get_datapath('Unihan_Readings.txt'),
        ]

        columns = [
            'kTotalStrokes',
            'kPhonetic',
            'kCantonese',
            'kDefinition',
        ] + process.default_columns

        items = process.convert(csv_files, columns)

        notInColumns = []

        for key, values in items.items():
            if any(v for v in values if v not in columns):
                for v in values:
                    if v not in columns:
                        notInColumns.append(v)

        self.assertEqual(
            [], notInColumns,
        )


class UnihanTestCase(UnihanHelper):
    """Utilities to retrieve unihan data in datapackage format."""

    def test_flatten_headings(self):

        single_dataset = {
            'Unihan_Readings.txt': [
                'kCantonese',
                'kDefinition',
                'kHangul',
            ]
        }

        expected = ['kCantonese', 'kDefinition', 'kHangul']
        results = process.get_headings(single_dataset)

        self.assertEqual(expected, results)

        datasets = {
            'Unihan_NumericValues.txt': [
                'kAccountingNumeric',
                'kOtherNumeric',
                'kPrimaryNumeric',
            ],
            'Unihan_OtherMappings.txt': [
                'kBigFive',
                'kCCCII',
                'kCNS1986',
            ]
        }

        expected = [
            'kAccountingNumeric',
            'kOtherNumeric',
            'kPrimaryNumeric',
            'kBigFive',
            'kCCCII',
            'kCNS1986',
        ]

        results = process.get_headings(datasets)

        self.assertSetEqual(set(expected), set(results))

    def test_pick_files(self):
        """Pick a white list of files to build from."""

        files = ['Unihan_Readings.txt', 'Unihan_Variants.txt']

        config = {
            'files': files
        }

        b = process.Builder(config)

        result = b.config.files
        expected = files

        self.assertEqual(result, expected, msg='Returns only the files picked.')



    def test_raise_error_unknown_heading(self):
        """Throw error if picking unknown heading."""

        config = {
            'headings': ['kHello']
        }

        with self.assertRaisesRegexp(KeyError, 'Heading ([a-zA-Z].*) not found in file list.'):
            b = process.Builder(config)

    def test_raise_error_unknown_file(self):
        """Throw error if picking unknown file."""

        config = {
            'files': ['Sparta.lol']
        }

        with self.assertRaisesRegexp(KeyError, 'File ([a-zA-Z].*) not found in file list.'):
            b = process.Builder(config)

    def test_raise_error_unknown_heading_filtered_files(self):
        """Throw error if picking heading not in file list, when files specified."""
        pass

    def test_set_reduce_files_automatically_when_only_heading_specified(self):
        """Picks file automatically if none specified and headings are."""

        headings = process.UNIHAN_MANIFEST['Unihan_Readings.txt'] + process.UNIHAN_MANIFEST['Unihan_Variants.txt']

        config = {
            'headings': headings
        }

        b = process.Builder(config)

        expected = ['Unihan_Readings.txt', 'Unihan_Variants.txt']
        result = b.config.files

        self.assertEqual(result, expected)

    def test_set_reduce_headings_automatically_when_only_files_specified(self):
        """Picks only necessary files when headings specified."""

        files = ['Unihan_Readings.txt', 'Unihan_Variants.txt']

        config = {
            'files': files
        }

        b = process.Builder(config)

        expected = process.get_headings(process.filter_manifest(files))
        result = b.config.headings

        self.assertEqual(result, expected, msg='Returns only the headings for files picked.')


class ProcessTestCase(TestCase):

    def test_conversion_ucn_to_utf8(self):
        pass


class CliArgTestCase(TestCase):
    """Allows for creating a custom output of unihan data
    in datapackage.json format."""

    def test_no_args(self):
        """Works without arguments."""

        expected = default_config
        result = Builder.from_cli([]).config

        self.assertEqual(expected, result)

    def test_cli_plus_defaults(self):
        """Test CLI args + defaults."""

        expectedIn = {'destination': 'data/output.csv'}
        result = Builder.from_cli(['-d', 'data/output.csv']).config
        self.assertDictContainsSubset(expectedIn, result)

        expectedIn = {'headings': ['kDefinition']}
        result = Builder.from_cli(['-H', 'kDefinition']).config
        self.assertDictContainsSubset(expectedIn, result)

        expectedIn = {'headings': ['kDefinition']}
        result = Builder.from_cli(['-H', 'kDefinition']).config
        self.assertDictContainsSubset(expectedIn, result)

        expectedIn = {'headings': ['kDefinition', 'kXerox']}
        result = Builder.from_cli(['-H', 'kDefinition', 'kXerox']).config
        self.assertDictContainsSubset(expectedIn, result, msg="Accepts multiple headings.")

        expectedIn = {'headings': ['kDefinition', 'kXerox'], 'destination': 'data/ha.csv'}
        result = Builder.from_cli(['-H', 'kDefinition', 'kXerox', '-d', 'data/ha.csv']).config
        self.assertDictContainsSubset(expectedIn, result, msg="Accepts multiple arguments.")

def suite():
    setup_path()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UnihanTestCase))
    suite.addTest(unittest.makeSuite(UnihanScriptsTestCase))
    suite.addTest(unittest.makeSuite(ProcessTestCase))
    suite.addTest(unittest.makeSuite(CliArgTestCase))
    return suite
