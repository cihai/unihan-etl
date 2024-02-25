"""Experimental pydantic models for unihan data."""
import typing as t

import pydantic

from unihan_etl.expansion import expand_kTGHZ2013


class UCNBaseModel(pydantic.BaseModel):
    """Core model for UCN data."""

    ucn: str


class kTGHZ2013Location(pydantic.BaseModel):
    """Core model for location."""

    page: int
    position: int
    entry_type: int = pydantic.Field(
        description=(
            "0 for a main entry and greater than 0 for a parenthesized or bracketed "
            + "variant of the main entry"
        )
    )


class kTGHZ2013Reading(pydantic.BaseModel):
    """kTGHZ2013 model."""

    reading: str
    locations: t.List[kTGHZ2013Location]


class kTGHZ2013(UCNBaseModel):
    """kTGHZ2013 model."""

    readings: t.List[kTGHZ2013Reading]

    model_config = pydantic.ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    @classmethod
    def from_string(cls, value: str) -> "kTGHZ2013":
        """Accept csv valdation from UNIHAN."""
        if isinstance(value, str):
            ucn, field, val = value.split("\t")
            outs = expand_kTGHZ2013(val.split(" "))

            return cls(
                ucn=ucn,
                readings=[
                    kTGHZ2013Reading(
                        reading=out["reading"],
                        locations=[
                            kTGHZ2013Location(
                                page=loc["page"],
                                position=loc["position"],
                                entry_type=loc["entry_type"],
                            )
                            for loc in out["locations"]
                        ],
                    )
                    for out in outs
                ],
            )
        elif isinstance(value, dict):
            return pydantic.parse_obj_as(cls, value)
        raise pydantic.ValidationError("Invalid input for kTGHZ2013 model.")  # noqa: TRY003
