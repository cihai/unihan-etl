# -*- coding: utf-8 -*-
"""Tests for unihan data download and processing."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import logging
import os
import shutil
import zipfile

import pytest

from scripts import process
from scripts._compat import text_type
from scripts.process import (UNIHAN_zip_path, Packager, default_options,
                             zip_has_files)
from scripts.test import assert_dict_contains_subset, get_datapath
from scripts.util import merge_dict, ucn_to_unicode, ucnstring_to_unicode

log = logging.getLogger(__name__)


SAMPLE_DATA = """\
U+3400	kCantonese	jau1
U+3400	kDefinition	(same as U+4E18 丘) hillock or mound
U+3400	kMandarin	qiū
U+3401	kCantonese	tim2
U+3401	kDefinition	to lick; to taste, a mat, bamboo bark
U+3401	kHanyuPinyin	10019.020:tiàn
"""

test_options = merge_dict(default_options.copy(), {
    'input_files': ['Unihan_Readings.txt'],
})


mock_zip_filename = 'Unihan.zip'


@pytest.fixture(scope="session")
def mock_test_dir(tmpdir_factory):
    fn = tmpdir_factory.mktemp('cihaidata_unihan')
    return fn


@pytest.fixture(scope="session")
def mock_zip_file(mock_test_dir):
    return mock_test_dir.join(mock_zip_filename)


@pytest.fixture(scope="session")
def mock_zip(mock_zip_file):
    zf = zipfile.ZipFile(str(mock_zip_file), 'a')
    zf.writestr("Unihan_Readings.txt", SAMPLE_DATA.encode('utf-8'))
    zf.close()
    return zf


@pytest.fixture(scope="session")
def TestPackager(mock_test_dir, mock_zip_file):
    # monkey-patching builder
    options = {
        'work_dir': str(mock_test_dir),
        'zip_path': str(mock_zip_file),
        'destination': str(
            mock_test_dir.join('unihan.csv')
        )
    }
    return Packager(options)


@pytest.mark.skip(reason="slow and may remove this")
def test_builder_mock(TestPackager):
    b = TestPackager

    assert test_options == b.options
    assert default_options != b.options


def test_zip_has_files(mock_zip):
    assert zip_has_files(['Unihan_Readings.txt'], mock_zip)

    assert not zip_has_files(['Unihan_Cats.txt'], mock_zip)


def test_has_valid_zip(tmpdir, mock_zip):
    if os.path.isfile(UNIHAN_zip_path):
        assert process.has_valid_zip(UNIHAN_zip_path)
    else:
        assert not process.has_valid_zip(UNIHAN_zip_path)

    assert process.has_valid_zip(mock_zip.filename)

    bad_zip = tmpdir.join('corrupt.zip')
    bad_zip.write('moo')

    assert not process.has_valid_zip(str(bad_zip))


def test_in_fields():
    columns = ['hey', 'kDefinition', 'kWhat']
    result = process.in_fields('kDefinition', columns)

    assert result


def test_filter_manifest():
    expected = {
        'Unihan_Variants.txt': [
            'kCompatibilityVariant',
            'kSemanticVariant',
            'kSimplifiedVariant',
            'kSpecializedSemanticVariant',
            'kTraditionalVariant',
            'kZVariant',
        ]
    }

    result = process.filter_manifest(['Unihan_Variants.txt'])

    assert set(result) == set(expected)


def test_get_files():
    fields = ['kKorean', 'kRSUnicode']
    expected = ['Unihan_Readings.txt', 'Unihan_RadicalStrokeCounts.txt']

    result = process.get_files(fields)

    assert set(result) == set(expected)


def test_save(tmpdir, mock_zip_file):
    dest_filepath = tmpdir.join(mock_zip_filename)
    process.save(str(mock_zip_file), str(dest_filepath), shutil.copy)

    assert os.path.exists(str(dest_filepath))


def test_download(tmpdir, mock_zip_file):
    dest_filepath = tmpdir.join('data', mock_zip_filename)

    process.download(str(mock_zip_file), str(dest_filepath), shutil.copy)

    result = os.path.dirname(str(dest_filepath.join('data')))
    assert result, "Creates data directory if doesn't exist."


def test_download_mock(monkeypatch, tmpdir, mock_zip_file):
    dest_filepath = tmpdir.join('data', 'hey.zip')

    def save(url, filename, url_retrieve, reporthook=None):
        mock_zip_file.copy(dest_filepath)
    monkeypatch.setattr(process, 'save', save)

    p = Packager(merge_dict(test_options.copy, {
        'fields': ['kDefinition'],
        'zip_path': str(dest_filepath),
        'work_dir': str(tmpdir)
    }))
    p.download()
    assert os.path.exists(str(dest_filepath))
    p.export


def test_extract_zip(mock_zip_file):
    zf = process.extract_zip(str(mock_zip_file))

    assert len(zf.infolist()) == 1
    assert zf.infolist()[0].file_size == 218
    assert zf.infolist()[0].filename == "Unihan_Readings.txt"


def test_export(mock_zip_file, mock_test_dir):
    process.export(
        zip_path=str(mock_zip_file),
        input_files=['Unihan_Readings.txt'],
        work_dir=str(mock_test_dir),
        fields=[
            'kTotalStrokes',
            'kPhonetic',
            'kCantonese',
            'kDefinition',
        ],
        destination=str(
            mock_test_dir.join('unihan.csv')
        )
    )


def test_normalize_only_output_requested_columns(tmpdir):
    csv_file = tmpdir.join('test.csv')

    csv_file.write(SAMPLE_DATA.encode('utf-8'), mode='wb')

    csv_files = [str(csv_file)]

    columns = [
        'kTotalStrokes',
        'kPhonetic',
        'kCantonese',
        'kDefinition',
    ]

    items = process.normalize_files(csv_files, columns)

    not_in_columns = []
    in_columns = ['kDefinition', 'kCantonese']

    # columns not selected in normalize must not be in result.
    for v in items[0]:
        if v not in columns:
            not_in_columns.append(v)
        else:
            in_columns.append(v)

    assert [] == not_in_columns, "normalize filters columns not specified."
    assert set(in_columns).issubset(set(columns)), (
        "normalize returns correct columns specified + ucn and char."
    )


def test_normalize_simple_data_format():
    """normalize turns data into simple data format (SDF)."""
    csv_files = [
        get_datapath('Unihan_DictionaryLikeData.txt'),
        get_datapath('Unihan_Readings.txt'),
    ]

    columns = [
        'kTotalStrokes',
        'kPhonetic',
        'kCantonese',
        'kDefinition',
    ] + process.INDEX_FIELDS

    items = process.normalize_files(csv_files, columns)

    header = items[0]
    assert header == columns

    rows = items[1:]  # NOQA


def test_flatten_fields():

    single_dataset = {
        'Unihan_Readings.txt': [
            'kCantonese',
            'kDefinition',
            'kHangul',
        ]
    }

    expected = ['kCantonese', 'kDefinition', 'kHangul']
    results = process.get_fields(single_dataset)

    assert expected == results

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

    results = process.get_fields(datasets)

    assert set(expected) == set(results)


def test_pick_files(mock_zip_file):
    """Pick a white list of files to build from."""

    files = ['Unihan_Readings.txt', 'Unihan_Variants.txt']

    options = {
        'input_files': files,
        'zip_path': str(mock_zip_file)
    }

    b = process.Packager(options)

    result = b.options['input_files']
    expected = files

    assert result == expected, 'Returns only the files picked.'


def test_raise_error_unknown_field():
    """Throw error if picking unknown field."""

    options = {
        'fields': ['kHello']
    }

    with pytest.raises(KeyError) as excinfo:
        process.Packager(options)
    excinfo.match('Field ([a-zA-Z].*) not found in file list.')


def test_raise_error_unknown_file():
    """Throw error if picking unknown file."""

    options = {
        'input_files': ['Sparta.lol']
    }

    with pytest.raises(KeyError) as excinfo:
        process.Packager(options)
    excinfo.match('File ([a-zA-Z_\.\'].*) not found in file list.')


def test_raise_error_unknown_field_filtered_files():
    """Throw error field not in file list, when files specified."""

    files = ['Unihan_Variants.txt']

    options = {
        'input_files': files,
        'fields': ['kDefinition'],
    }

    with pytest.raises(KeyError) as excinfo:
        process.Packager(options)
    excinfo.match('Field ([a-zA-Z].*) not found in file list.')


def test_set_reduce_files_automatically_when_only_field_specified():
    """Picks file automatically if none specified and fields are."""

    fields = (
        process.UNIHAN_MANIFEST['Unihan_Readings.txt'] +
        process.UNIHAN_MANIFEST['Unihan_Variants.txt']
    )

    options = {
        'fields': fields,
    }

    b = process.Packager(options)

    expected = ['Unihan_Readings.txt', 'Unihan_Variants.txt']
    results = b.options['input_files']

    assert set(expected) == set(results)


def test_set_reduce_fields_automatically_when_only_files_specified():
    """Picks only necessary files when fields specified."""

    files = ['Unihan_Readings.txt', 'Unihan_Variants.txt']

    options = {
        'input_files': files
    }

    b = process.Packager(options)

    results = process.get_fields(process.filter_manifest(files))
    expected = b.options['fields']

    assert set(expected) == set(results), (
        'Returns only the fields for files picked.'
    )


def test_conversion_ucn_to_unicode():
    before = 'U+4E00'
    expected = '\u4e00'

    result = ucn_to_unicode(before)

    assert result == expected

    assert isinstance(result, text_type)

    # wide character
    before = 'U+20001'
    expected = '\U00020001'

    result = ucn_to_unicode(before)

    assert result == expected
    assert isinstance(result, text_type)

    before = '(same as U+7A69 穩) firm; stable; secure'
    expected = '(same as 穩 穩) firm; stable; secure'

    result = ucnstring_to_unicode(before)

    assert result == expected
    assert isinstance(result, text_type)


def test_no_args():
    """Works without arguments."""

    assert default_options == Packager.from_cli([]).options


def test_cli_plus_defaults(mock_zip_file):
    """Test CLI args + defaults."""

    expected_in = {'zip_path': str(mock_zip_file)}
    result = Packager.from_cli(['-z', str(mock_zip_file)]).options
    assert_dict_contains_subset(expected_in, result)

    expected_in = {'fields': ['kDefinition']}
    result = Packager.from_cli(['-f', 'kDefinition']).options
    assert_dict_contains_subset(expected_in, result)

    expected_in = {'fields': ['kDefinition', 'kXerox']}
    result = Packager.from_cli(['-f', 'kDefinition', 'kXerox']).options
    assert_dict_contains_subset(
        expected_in, result, msg="Accepts multiple fields."
    )

    expected_in = {
        'fields': ['kDefinition', 'kXerox'], 'destination': 'data/ha.csv'
    }
    result = Packager.from_cli(
        ['-f', 'kDefinition', 'kXerox', '-d', 'data/ha.csv']).options
    assert_dict_contains_subset(
        expected_in, result, msg="Accepts multiple arguments."
    )


def test_cli_exit_emessage_to_stderr():
    """Sends exception .message to stderr on exit."""

    # SystemExit print's to stdout by default
    with pytest.raises(SystemExit) as excinfo:
        Packager.from_cli(['-d', 'data/output.csv', '-f', 'sdfa'])

    excinfo.match('Field sdfa not found in file list.')
