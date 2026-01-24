"""Tests for fields subcommand."""

from __future__ import annotations

import json
import typing as t

import pytest

from unihan_etl.cli.fields import get_fields_data


class GetFieldsDataFixture(t.NamedTuple):
    """Test fixture for get_fields_data function."""

    test_id: str
    input_files: list[str] | None
    expect_non_empty: bool
    expect_field_names: list[str]


GET_FIELDS_DATA_FIXTURES: list[GetFieldsDataFixture] = [
    GetFieldsDataFixture(
        test_id="all_fields",
        input_files=None,
        expect_non_empty=True,
        expect_field_names=["kDefinition", "kMandarin"],
    ),
    GetFieldsDataFixture(
        test_id="filter_by_readings_file",
        input_files=["Unihan_Readings.txt"],
        expect_non_empty=True,
        expect_field_names=["kDefinition", "kMandarin"],
    ),
    GetFieldsDataFixture(
        test_id="filter_by_numeric_file",
        input_files=["Unihan_NumericValues.txt"],
        expect_non_empty=True,
        expect_field_names=["kAccountingNumeric", "kPrimaryNumeric"],
    ),
    GetFieldsDataFixture(
        test_id="nonexistent_file_returns_empty",
        input_files=["NonexistentFile.txt"],
        expect_non_empty=False,
        expect_field_names=[],
    ),
]


@pytest.mark.parametrize(
    GetFieldsDataFixture._fields,
    GET_FIELDS_DATA_FIXTURES,
    ids=[f.test_id for f in GET_FIELDS_DATA_FIXTURES],
)
def test_get_fields_data(
    test_id: str,
    input_files: list[str] | None,
    expect_non_empty: bool,
    expect_field_names: list[str],
) -> None:
    """Test get_fields_data returns correct field data."""
    result = get_fields_data(input_files)

    if expect_non_empty:
        assert len(result) > 0
        # All records should have 'name' and 'file' keys
        for record in result:
            assert "name" in record
            assert "file" in record
        # Check expected fields are present
        field_names = [r["name"] for r in result]
        for expected_name in expect_field_names:
            assert expected_name in field_names
    else:
        assert len(result) == 0


class FieldsRecordStructureFixture(t.NamedTuple):
    """Test fixture for fields record structure."""

    test_id: str
    expected_keys: list[str]


FIELDS_RECORD_STRUCTURE_FIXTURES: list[FieldsRecordStructureFixture] = [
    FieldsRecordStructureFixture(
        test_id="has_name_and_file_keys",
        expected_keys=["name", "file"],
    ),
]


@pytest.mark.parametrize(
    FieldsRecordStructureFixture._fields,
    FIELDS_RECORD_STRUCTURE_FIXTURES,
    ids=[f.test_id for f in FIELDS_RECORD_STRUCTURE_FIXTURES],
)
def test_fields_record_structure(
    test_id: str,
    expected_keys: list[str],
) -> None:
    """Test fields data records have expected structure."""
    result = get_fields_data()

    assert len(result) > 0
    for record in result:
        for key in expected_keys:
            assert key in record


def test_fields_data_sorted_by_name() -> None:
    """Test fields data is sorted alphabetically by field name."""
    result = get_fields_data()

    names = [r["name"] for r in result]
    assert names == sorted(names)


def test_fields_data_json_serializable() -> None:
    """Test fields data can be serialized to JSON."""
    result = get_fields_data()

    # Should not raise
    json_output = json.dumps(result)
    assert isinstance(json_output, str)

    # Round-trip should work
    parsed = json.loads(json_output)
    assert parsed == result
