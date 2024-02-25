"""Test expansion of multi-value fields in UNIHAN."""
import typing as t

from unihan_etl import validator

if t.TYPE_CHECKING:
    pass


def test_kTGHZ2013() -> None:
    """Example of kTGHZ2013 being parsed via pydantic."""
    model = validator.kTGHZ2013.from_string("U+3447	kTGHZ2013	482.140:zhòu")
    assert model.ucn == "U+3447"

    model = validator.kTGHZ2013.from_string(
        "U+4E07	kTGHZ2013	256.090:mò 379.160:wàn"
    )
    assert model.ucn == "U+4E07"
    assert model.readings[0].reading == "mò"
    assert model.readings[1].reading == "wàn"
    assert model.readings[1].locations[0] == validator.kTGHZ2013Location(
        page=379,
        position=16,
        entry_type=0,
    )

    print(f"\n{model}\n")
