"""Tests for files subcommand."""

from __future__ import annotations

import json
import typing as t

import pytest

from unihan_etl.cli.files import get_files_data


class GetFilesDataFixture(t.NamedTuple):
    """Test fixture for get_files_data function."""

    test_id: str
    with_fields: bool
    expect_fields_key: bool


GET_FILES_DATA_FIXTURES: list[GetFilesDataFixture] = [
    GetFilesDataFixture(
        test_id="without_fields",
        with_fields=False,
        expect_fields_key=False,
    ),
    GetFilesDataFixture(
        test_id="with_fields",
        with_fields=True,
        expect_fields_key=True,
    ),
]


@pytest.mark.parametrize(
    GetFilesDataFixture._fields,
    GET_FILES_DATA_FIXTURES,
    ids=[f.test_id for f in GET_FILES_DATA_FIXTURES],
)
def test_get_files_data(
    test_id: str,
    with_fields: bool,
    expect_fields_key: bool,
) -> None:
    """Test get_files_data returns correct file data."""
    result = get_files_data(with_fields)

    assert len(result) > 0
    for record in result:
        assert "name" in record
        assert "field_count" in record
        if expect_fields_key:
            assert "fields" in record
            assert isinstance(record["fields"], list)
        else:
            assert "fields" not in record


class ExpectedFilesFixture(t.NamedTuple):
    """Test fixture for expected UNIHAN files."""

    test_id: str
    expected_file_names: list[str]


EXPECTED_FILES_FIXTURES: list[ExpectedFilesFixture] = [
    ExpectedFilesFixture(
        test_id="has_readings_file",
        expected_file_names=["Unihan_Readings.txt"],
    ),
    ExpectedFilesFixture(
        test_id="has_dictionary_files",
        expected_file_names=[
            "Unihan_DictionaryIndices.txt",
            "Unihan_DictionaryLikeData.txt",
        ],
    ),
    ExpectedFilesFixture(
        test_id="has_numeric_file",
        expected_file_names=["Unihan_NumericValues.txt"],
    ),
]


@pytest.mark.parametrize(
    ExpectedFilesFixture._fields,
    EXPECTED_FILES_FIXTURES,
    ids=[f.test_id for f in EXPECTED_FILES_FIXTURES],
)
def test_expected_files_present(
    test_id: str,
    expected_file_names: list[str],
) -> None:
    """Test expected UNIHAN files are present in output."""
    result = get_files_data()

    file_names = [r["name"] for r in result]
    for expected_name in expected_file_names:
        assert expected_name in file_names


def test_files_data_sorted_by_name() -> None:
    """Test files data is sorted alphabetically by file name."""
    result = get_files_data()

    names = [r["name"] for r in result]
    assert names == sorted(names)


def test_files_field_count_matches_fields_list() -> None:
    """Test field_count matches length of fields list when included."""
    result = get_files_data(with_fields=True)

    for record in result:
        assert record["field_count"] == len(record["fields"])


def test_files_data_json_serializable() -> None:
    """Test files data can be serialized to JSON."""
    result = get_files_data(with_fields=True)

    # Should not raise
    json_output = json.dumps(result)
    assert isinstance(json_output, str)

    # Round-trip should work
    parsed = json.loads(json_output)
    assert parsed == result


def test_files_field_count_positive() -> None:
    """Test all files have positive field counts."""
    result = get_files_data()

    for record in result:
        assert record["field_count"] > 0
