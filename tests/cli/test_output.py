"""Tests for CLI output formatting utilities."""

from __future__ import annotations

import io
import json
import typing as t

import pytest

from unihan_etl.cli._output import (
    OutputFormat,
    add_output_arguments,
    format_json,
    format_ndjson,
    format_output,
    format_table,
    get_output_format_from_args,
    print_output,
)


class FormatJsonFixture(t.NamedTuple):
    """Test fixture for JSON formatting."""

    test_id: str
    data: list[dict[str, t.Any]] | dict[str, t.Any]
    expected_type: type


FORMAT_JSON_FIXTURES: list[FormatJsonFixture] = [
    FormatJsonFixture(
        test_id="single_dict",
        data={"name": "test", "value": 42},
        expected_type=dict,
    ),
    FormatJsonFixture(
        test_id="list_of_dicts",
        data=[{"name": "a"}, {"name": "b"}],
        expected_type=list,
    ),
    FormatJsonFixture(
        test_id="empty_list",
        data=[],
        expected_type=list,
    ),
]


@pytest.mark.parametrize(
    FormatJsonFixture._fields,
    FORMAT_JSON_FIXTURES,
    ids=[f.test_id for f in FORMAT_JSON_FIXTURES],
)
def test_format_json(
    test_id: str,
    data: list[dict[str, t.Any]] | dict[str, t.Any],
    expected_type: type,
) -> None:
    """Test JSON formatting produces valid JSON."""
    result = format_json(data)

    # Parse result back to verify validity
    parsed = json.loads(result)
    assert isinstance(parsed, expected_type)


class FormatNdjsonFixture(t.NamedTuple):
    """Test fixture for NDJSON formatting."""

    test_id: str
    data: list[dict[str, t.Any]]
    expected_line_count: int


FORMAT_NDJSON_FIXTURES: list[FormatNdjsonFixture] = [
    FormatNdjsonFixture(
        test_id="single_record",
        data=[{"name": "test"}],
        expected_line_count=1,
    ),
    FormatNdjsonFixture(
        test_id="two_records",
        data=[{"name": "a"}, {"name": "b"}],
        expected_line_count=2,
    ),
    FormatNdjsonFixture(
        test_id="three_records",
        data=[{"id": 1}, {"id": 2}, {"id": 3}],
        expected_line_count=3,
    ),
]


@pytest.mark.parametrize(
    FormatNdjsonFixture._fields,
    FORMAT_NDJSON_FIXTURES,
    ids=[f.test_id for f in FORMAT_NDJSON_FIXTURES],
)
def test_format_ndjson(
    test_id: str,
    data: list[dict[str, t.Any]],
    expected_line_count: int,
) -> None:
    """Test NDJSON formatting produces one JSON per line."""
    result = format_ndjson(data)
    lines = [line for line in result.strip().split("\n") if line]

    assert len(lines) == expected_line_count

    # Each line should be valid JSON
    for line in lines:
        parsed = json.loads(line)
        assert isinstance(parsed, dict)


class FormatTableFixture(t.NamedTuple):
    """Test fixture for table formatting."""

    test_id: str
    data: list[dict[str, t.Any]]
    headers: list[str] | None
    expected_contains: list[str]


FORMAT_TABLE_FIXTURES: list[FormatTableFixture] = [
    FormatTableFixture(
        test_id="simple_table",
        data=[{"name": "test", "value": 42}],
        headers=["name", "value"],
        expected_contains=["name", "value", "test", "42"],
    ),
    FormatTableFixture(
        test_id="auto_headers",
        data=[{"col1": "a", "col2": "b"}],
        headers=None,
        expected_contains=["col1", "col2", "a", "b"],
    ),
    FormatTableFixture(
        test_id="multiple_rows",
        data=[{"field": "kDefinition"}, {"field": "kMandarin"}],
        headers=["field"],
        expected_contains=["field", "kDefinition", "kMandarin"],
    ),
]


@pytest.mark.parametrize(
    FormatTableFixture._fields,
    FORMAT_TABLE_FIXTURES,
    ids=[f.test_id for f in FORMAT_TABLE_FIXTURES],
)
def test_format_table(
    test_id: str,
    data: list[dict[str, t.Any]],
    headers: list[str] | None,
    expected_contains: list[str],
) -> None:
    """Test table formatting produces readable output."""
    result = format_table(data, headers=headers)

    for expected in expected_contains:
        assert expected in result


class FormatOutputFixture(t.NamedTuple):
    """Test fixture for format_output dispatch."""

    test_id: str
    data: list[dict[str, t.Any]]
    output_format: OutputFormat
    validation_fn: str  # Method name to call on result


FORMAT_OUTPUT_FIXTURES: list[FormatOutputFixture] = [
    FormatOutputFixture(
        test_id="json_format",
        data=[{"name": "test"}],
        output_format=OutputFormat.JSON,
        validation_fn="startswith",
    ),
    FormatOutputFixture(
        test_id="ndjson_format",
        data=[{"name": "test"}],
        output_format=OutputFormat.NDJSON,
        validation_fn="strip",
    ),
    FormatOutputFixture(
        test_id="table_format",
        data=[{"name": "test"}],
        output_format=OutputFormat.TABLE,
        validation_fn="strip",
    ),
]


@pytest.mark.parametrize(
    FormatOutputFixture._fields,
    FORMAT_OUTPUT_FIXTURES,
    ids=[f.test_id for f in FORMAT_OUTPUT_FIXTURES],
)
def test_format_output(
    test_id: str,
    data: list[dict[str, t.Any]],
    output_format: OutputFormat,
    validation_fn: str,
) -> None:
    """Test format_output dispatches correctly."""
    result = format_output(data, output_format)
    assert isinstance(result, str)
    assert len(result) > 0


class PrintOutputFixture(t.NamedTuple):
    """Test fixture for print_output function."""

    test_id: str
    data: list[dict[str, t.Any]]
    output_format: OutputFormat
    expected_in_output: list[str]


PRINT_OUTPUT_FIXTURES: list[PrintOutputFixture] = [
    PrintOutputFixture(
        test_id="print_json",
        data=[{"field": "kDefinition", "file": "Unihan_Readings.txt"}],
        output_format=OutputFormat.JSON,
        expected_in_output=['"field":', '"kDefinition"'],
    ),
    PrintOutputFixture(
        test_id="print_ndjson",
        data=[{"field": "kDefinition"}, {"field": "kMandarin"}],
        output_format=OutputFormat.NDJSON,
        expected_in_output=["kDefinition", "kMandarin"],
    ),
    PrintOutputFixture(
        test_id="print_table",
        data=[{"name": "test", "count": 5}],
        output_format=OutputFormat.TABLE,
        expected_in_output=["name", "count", "test", "5"],
    ),
]


@pytest.mark.parametrize(
    PrintOutputFixture._fields,
    PRINT_OUTPUT_FIXTURES,
    ids=[f.test_id for f in PRINT_OUTPUT_FIXTURES],
)
def test_print_output(
    test_id: str,
    data: list[dict[str, t.Any]],
    output_format: OutputFormat,
    expected_in_output: list[str],
) -> None:
    """Test print_output writes to file correctly."""
    buffer = io.StringIO()
    print_output(data, output_format, file=buffer)

    output = buffer.getvalue()
    for expected in expected_in_output:
        assert expected in output


def test_output_format_enum_values() -> None:
    """Test OutputFormat enum has expected values."""
    assert OutputFormat.TABLE.value == "table"
    assert OutputFormat.JSON.value == "json"
    assert OutputFormat.NDJSON.value == "ndjson"


def test_add_output_arguments() -> None:
    """Test add_output_arguments adds --json and --ndjson flags."""
    import argparse

    parser = argparse.ArgumentParser()
    add_output_arguments(parser)

    # Parse with --json
    args_json = parser.parse_args(["--json"])
    assert args_json.json is True
    assert args_json.ndjson is False

    # Parse with --ndjson
    args_ndjson = parser.parse_args(["--ndjson"])
    assert args_ndjson.json is False
    assert args_ndjson.ndjson is True

    # Parse with neither
    args_default = parser.parse_args([])
    assert args_default.json is False
    assert args_default.ndjson is False


class GetOutputFormatFixture(t.NamedTuple):
    """Test fixture for get_output_format_from_args."""

    test_id: str
    json_flag: bool
    ndjson_flag: bool
    expected_format: OutputFormat


GET_OUTPUT_FORMAT_FIXTURES: list[GetOutputFormatFixture] = [
    GetOutputFormatFixture(
        test_id="default_is_table",
        json_flag=False,
        ndjson_flag=False,
        expected_format=OutputFormat.TABLE,
    ),
    GetOutputFormatFixture(
        test_id="json_flag_set",
        json_flag=True,
        ndjson_flag=False,
        expected_format=OutputFormat.JSON,
    ),
    GetOutputFormatFixture(
        test_id="ndjson_flag_set",
        json_flag=False,
        ndjson_flag=True,
        expected_format=OutputFormat.NDJSON,
    ),
]


@pytest.mark.parametrize(
    GetOutputFormatFixture._fields,
    GET_OUTPUT_FORMAT_FIXTURES,
    ids=[f.test_id for f in GET_OUTPUT_FORMAT_FIXTURES],
)
def test_get_output_format_from_args(
    test_id: str,
    json_flag: bool,
    ndjson_flag: bool,
    expected_format: OutputFormat,
) -> None:
    """Test get_output_format_from_args returns correct format."""
    import argparse

    args = argparse.Namespace(json=json_flag, ndjson=ndjson_flag)
    result = get_output_format_from_args(args)
    assert result == expected_format
