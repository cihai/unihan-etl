"""Tests for main CLI entry point."""

from __future__ import annotations

import typing as t

import pytest

from unihan_etl.cli import cli, create_parser


class CLIHelpFixture(t.NamedTuple):
    """Test fixture for CLI help output."""

    test_id: str
    args: list[str]
    expected_in_output: list[str]


CLI_HELP_FIXTURES: list[CLIHelpFixture] = [
    CLIHelpFixture(
        test_id="main_help_shows_subcommands",
        args=["--help"],
        expected_in_output=["export", "download", "fields", "files", "search"],
    ),
    CLIHelpFixture(
        test_id="export_help",
        args=["export", "--help"],
        expected_in_output=["Export UNIHAN data", "-F", "--format"],
    ),
    CLIHelpFixture(
        test_id="download_help",
        args=["download", "--help"],
        expected_in_output=["Download", "--source", "--zip-path"],
    ),
    CLIHelpFixture(
        test_id="fields_help",
        args=["fields", "--help"],
        expected_in_output=["List available UNIHAN fields", "--json", "--ndjson"],
    ),
    CLIHelpFixture(
        test_id="files_help",
        args=["files", "--help"],
        expected_in_output=["List available UNIHAN source files", "--with-fields"],
    ),
    CLIHelpFixture(
        test_id="search_help",
        args=["search", "--help"],
        expected_in_output=["Look up", "char", "--json", "--ndjson"],
    ),
]


@pytest.mark.parametrize(
    CLIHelpFixture._fields,
    CLI_HELP_FIXTURES,
    ids=[f.test_id for f in CLI_HELP_FIXTURES],
)
def test_cli_help_output(
    test_id: str,
    args: list[str],
    expected_in_output: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test CLI help output contains expected content."""
    with pytest.raises(SystemExit) as exc_info:
        cli(args)

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    for expected in expected_in_output:
        assert expected in captured.out


class CLINoArgsFixture(t.NamedTuple):
    """Test fixture for CLI with no arguments."""

    test_id: str
    args: list[str]
    expected_exit_code: int


CLI_NO_ARGS_FIXTURES: list[CLINoArgsFixture] = [
    CLINoArgsFixture(
        test_id="no_args_shows_help",
        args=[],
        expected_exit_code=0,
    ),
]


@pytest.mark.parametrize(
    CLINoArgsFixture._fields,
    CLI_NO_ARGS_FIXTURES,
    ids=[f.test_id for f in CLI_NO_ARGS_FIXTURES],
)
def test_cli_no_args(
    test_id: str,
    args: list[str],
    expected_exit_code: int,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test CLI with no arguments shows help."""
    result = cli(args)

    assert result == expected_exit_code

    captured = capsys.readouterr()
    # Should show usage info
    assert "usage:" in captured.out or "unihan-etl" in captured.out


class CLIVersionFixture(t.NamedTuple):
    """Test fixture for CLI version output."""

    test_id: str
    args: list[str]


CLI_VERSION_FIXTURES: list[CLIVersionFixture] = [
    CLIVersionFixture(
        test_id="version_short",
        args=["-V"],
    ),
    CLIVersionFixture(
        test_id="version_long",
        args=["--version"],
    ),
]


@pytest.mark.parametrize(
    CLIVersionFixture._fields,
    CLI_VERSION_FIXTURES,
    ids=[f.test_id for f in CLI_VERSION_FIXTURES],
)
def test_cli_version(
    test_id: str,
    args: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test CLI version output."""
    with pytest.raises(SystemExit) as exc_info:
        cli(args)

    assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "unihan-etl" in captured.out


class ParserSubcommandFixture(t.NamedTuple):
    """Test fixture for parser subcommand configuration."""

    test_id: str
    subcommand: str


PARSER_SUBCOMMAND_FIXTURES: list[ParserSubcommandFixture] = [
    ParserSubcommandFixture(
        test_id="export_subcommand",
        subcommand="export",
    ),
    ParserSubcommandFixture(
        test_id="download_subcommand",
        subcommand="download",
    ),
    ParserSubcommandFixture(
        test_id="fields_subcommand",
        subcommand="fields",
    ),
    ParserSubcommandFixture(
        test_id="files_subcommand",
        subcommand="files",
    ),
    ParserSubcommandFixture(
        test_id="search_subcommand",
        subcommand="search",
    ),
]


@pytest.mark.parametrize(
    ParserSubcommandFixture._fields,
    PARSER_SUBCOMMAND_FIXTURES,
    ids=[f.test_id for f in PARSER_SUBCOMMAND_FIXTURES],
)
def test_parser_has_subcommand(
    test_id: str,
    subcommand: str,
) -> None:
    """Test parser has expected subcommands."""
    parser = create_parser()

    # Parse subcommand
    cmd_args = [subcommand] if subcommand != "search" else ["search", "一"]
    args = parser.parse_args(cmd_args)
    assert args.subparser_name == subcommand


def test_parser_global_options() -> None:
    """Test parser has global options."""
    parser = create_parser()

    # Color option
    args = parser.parse_args(["--color", "never", "fields"])
    assert args.color == "never"

    # Log level option
    args = parser.parse_args(["--log-level", "DEBUG", "fields"])
    assert args.log_level == "DEBUG"


def test_cli_fields_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test fields command with JSON output."""
    result = cli(["fields", "--json"])

    assert result == 0

    captured = capsys.readouterr()
    # Should be valid JSON array
    assert captured.out.strip().startswith("[")
    assert '"name":' in captured.out


def test_cli_fields_ndjson_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test fields command with NDJSON output."""
    result = cli(["fields", "--ndjson"])

    assert result == 0

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    # Each line should be valid JSON
    assert len(lines) > 0
    for line in lines:
        assert line.startswith("{")
        assert '"name":' in line


def test_cli_files_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test files command with JSON output."""
    result = cli(["files", "--json"])

    assert result == 0

    captured = capsys.readouterr()
    # Should be valid JSON array
    assert captured.out.strip().startswith("[")
    assert '"name":' in captured.out


def test_cli_files_with_fields(capsys: pytest.CaptureFixture[str]) -> None:
    """Test files command with --with-fields option."""
    result = cli(["files", "--with-fields", "--json"])

    assert result == 0

    captured = capsys.readouterr()
    assert '"fields":' in captured.out
