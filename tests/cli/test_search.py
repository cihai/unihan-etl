"""Tests for search subcommand."""

from __future__ import annotations

import typing as t

import pytest

from unihan_etl.cli.search import char_to_ucn, normalize_char_input


class NormalizeCharInputFixture(t.NamedTuple):
    """Test fixture for normalize_char_input function."""

    test_id: str
    input_value: str
    expected_char: str


NORMALIZE_CHAR_INPUT_FIXTURES: list[NormalizeCharInputFixture] = [
    NormalizeCharInputFixture(
        test_id="single_character",
        input_value="一",
        expected_char="一",
    ),
    NormalizeCharInputFixture(
        test_id="ucn_format_uppercase",
        input_value="U+4E00",
        expected_char="一",
    ),
    NormalizeCharInputFixture(
        test_id="hex_codepoint_only",
        input_value="4E00",
        expected_char="一",
    ),
    NormalizeCharInputFixture(
        test_id="hex_codepoint_lowercase",
        input_value="4e00",
        expected_char="一",
    ),
    NormalizeCharInputFixture(
        test_id="ucn_without_plus",
        input_value="U4E00",
        expected_char="一",
    ),
    NormalizeCharInputFixture(
        test_id="wide_character_ucn",
        input_value="U+20000",
        expected_char="\U00020000",
    ),
    NormalizeCharInputFixture(
        test_id="with_whitespace",
        input_value="  一  ",
        expected_char="一",
    ),
]


@pytest.mark.parametrize(
    NormalizeCharInputFixture._fields,
    NORMALIZE_CHAR_INPUT_FIXTURES,
    ids=[f.test_id for f in NORMALIZE_CHAR_INPUT_FIXTURES],
)
def test_normalize_char_input(
    test_id: str,
    input_value: str,
    expected_char: str,
) -> None:
    """Test normalize_char_input converts various formats to character."""
    result = normalize_char_input(input_value)
    assert result == expected_char


class InvalidCharInputFixture(t.NamedTuple):
    """Test fixture for invalid character inputs."""

    test_id: str
    input_value: str


INVALID_CHAR_INPUT_FIXTURES: list[InvalidCharInputFixture] = [
    InvalidCharInputFixture(
        test_id="invalid_string",
        input_value="invalid",
    ),
    InvalidCharInputFixture(
        test_id="multiple_characters",
        input_value="一二",
    ),
    InvalidCharInputFixture(
        test_id="empty_string",
        input_value="",
    ),
]


@pytest.mark.parametrize(
    InvalidCharInputFixture._fields,
    INVALID_CHAR_INPUT_FIXTURES,
    ids=[f.test_id for f in INVALID_CHAR_INPUT_FIXTURES],
)
def test_normalize_char_input_invalid(
    test_id: str,
    input_value: str,
) -> None:
    """Test normalize_char_input raises ValueError for invalid input."""
    with pytest.raises(ValueError, match="Cannot parse character input"):
        normalize_char_input(input_value)


class CharToUcnFixture(t.NamedTuple):
    """Test fixture for char_to_ucn function."""

    test_id: str
    input_char: str
    expected_ucn: str


CHAR_TO_UCN_FIXTURES: list[CharToUcnFixture] = [
    CharToUcnFixture(
        test_id="basic_cjk_character",
        input_char="一",
        expected_ucn="U+4E00",
    ),
    CharToUcnFixture(
        test_id="another_cjk_character",
        input_char="中",
        expected_ucn="U+4E2D",
    ),
    CharToUcnFixture(
        test_id="ascii_character",
        input_char="A",
        expected_ucn="U+0041",
    ),
    CharToUcnFixture(
        test_id="wide_character",
        input_char="\U00020000",
        expected_ucn="U+20000",
    ),
]


@pytest.mark.parametrize(
    CharToUcnFixture._fields,
    CHAR_TO_UCN_FIXTURES,
    ids=[f.test_id for f in CHAR_TO_UCN_FIXTURES],
)
def test_char_to_ucn(
    test_id: str,
    input_char: str,
    expected_ucn: str,
) -> None:
    """Test char_to_ucn converts character to UCN format."""
    result = char_to_ucn(input_char)
    assert result == expected_ucn


def test_round_trip_normalize_and_ucn() -> None:
    """Test round trip: normalize input -> char_to_ucn -> normalize again."""
    original_ucn = "U+4E00"

    # UCN -> char
    char = normalize_char_input(original_ucn)
    assert char == "一"

    # char -> UCN
    result_ucn = char_to_ucn(char)
    assert result_ucn == original_ucn

    # UCN -> char again
    char_again = normalize_char_input(result_ucn)
    assert char_again == char


def test_normalize_strips_whitespace() -> None:
    """Test normalize_char_input strips leading/trailing whitespace."""
    result = normalize_char_input("   U+4E00   ")
    assert result == "一"


def test_ucn_format_is_uppercase() -> None:
    """Test char_to_ucn produces uppercase hex digits."""
    result = char_to_ucn("一")
    # Should be U+4E00 not U+4e00
    assert result == "U+4E00"
    assert result.isupper() or "+" in result  # + is not a letter
