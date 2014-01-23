# -*- coding: utf-8 -*-
"""Tests for unihan.

cihaidata_unihan.testsuite.unihan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unihan

id char ucn colName colNmae colName

load csv's mapped by colNmae and individual names into a dict.

'中' {
    'ucn': '',
    'kDefinition': ''
}

1. insert dict/struct of { 'unihanFileName': ['colName', 'colName'] }
return cols, records

    Idea: Create a special iter class for it.
    Idea 2: Function, return cols, struct above

What a data set should provide.

1. Download the code.
2. Extract it (if necessary).
3. Extract the code

Get Cihai test object working with the local package directory files.

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

import sqlalchemy

from sqlalchemy import Table, MetaData

import cihai

from cihai.testsuite.cihai import CihaiHelper
from cihai.testsuite.helpers import TestCase
from cihai.util import get_datafile
from cihai.datasets import unihan
from cihai._compat import StringIO, text_type
from cihai import Cihai, CihaiDataset

from scripts import process

log = logging.getLogger(__name__)


class UnihanHelper(CihaiHelper):

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

    def test_in_columns(self):
        columns = ['hey', 'kDefinition', 'kWhat']
        result = process.in_columns('kDefinition', columns)

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

        u = self.cihai.use(unihan.Unihan)

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
    """Utilities to retrieve cihai information in a relational-friendly format.
    """

    def test_flatten_datasets(self):

        flatten_datasets = unihan.flatten_datasets

        single_dataset = {
            'Unihan_Readings.txt': [
                'kCantonese',
                'kDefinition',
                'kHangul',
            ]
        }

        expected = ['kCantonese', 'kDefinition', 'kHangul']
        results = flatten_datasets(single_dataset)

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

        results = flatten_datasets(datasets)

        self.assertSetEqual(set(expected), set(results))


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


def get_datapath(filename):

    return os.path.join(
        os.path.dirname(__file__), 'fixtures', filename
    )


def setup_path():
    script_path = os.path.join(
        os.path.dirname(__file__), os.pardir, 'scripts'
    )
    add_to_path(script_path)


def suite():
    setup_path()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UnihanTestCase))
    suite.addTest(unittest.makeSuite(UnihanScriptsTestCase))
    return suite
