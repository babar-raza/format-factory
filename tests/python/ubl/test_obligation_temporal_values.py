"""UBL-VALUES-001, temporal half: lexical and timezone preservation.

  "Preserve timezone and lexical precision of date/time values; expose explicit
   rounding policies for calculations."

This is the half of the capability the value-types slice did not build. It is
the one most libraries get wrong, because the obvious implementation --
`datetime.fromisoformat`, keep the datetime, format it back on write -- destroys
information that a business document asserted:

* `Z` and `+00:00` are the same instant and different lexical forms. A payment
  term recorded as `Z` that comes back as `+00:00` is a modified document.
* `10:00:00`, `10:00:00.0` and `10:00:00.000` are the same instant with three
  different declared precisions.
* A naive value has no timezone; inventing one asserts an offset the document
  never stated, and the wrong one changes the day.

So these types keep the original lexical form verbatim and expose the parsed
instant separately, rather than reconstructing the text from the instant.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from format_factory.ubl import UblDate, UblDateTime, UblTime, UblValidationError


# ── Lexical form survives verbatim ─────────────────────────────────────────


@pytest.mark.parametrize(
    "lexical",
    [
        "2026-08-05T10:00:00+02:00",
        "2026-08-05T10:00:00Z",
        "2026-08-05T10:00:00.000+02:00",
        "2026-08-05T10:00:00.0Z",
        "2026-08-05T10:00:00.123456-05:30",
        "2026-08-05T10:00:00",
        "2026-08-05T00:00:00Z",
    ],
)
def test_a_date_time_round_trips_its_exact_lexical_form(lexical: str) -> None:
    assert str(UblDateTime(lexical)) == lexical


def test_z_is_not_rewritten_as_an_offset() -> None:
    """The single most common silent modification. Same instant, different
    lexical form, and a document that said Z must still say Z."""
    value = UblDateTime("2026-08-05T10:00:00Z")

    assert str(value) == "2026-08-05T10:00:00Z"
    assert "+00:00" not in str(value)


def test_an_offset_of_zero_is_not_rewritten_as_z() -> None:
    """The converse, which a naive normalisation would also get wrong."""
    assert str(UblDateTime("2026-08-05T10:00:00+00:00")) == "2026-08-05T10:00:00+00:00"


@pytest.mark.parametrize(
    "lexical,digits",
    [
        ("2026-08-05T10:00:00Z", 0),
        ("2026-08-05T10:00:00.0Z", 1),
        ("2026-08-05T10:00:00.000Z", 3),
        ("2026-08-05T10:00:00.123456Z", 6),
    ],
)
def test_declared_fractional_precision_is_preserved(lexical: str, digits: int) -> None:
    """Trailing zeros in a fraction are a precision claim, not noise."""
    value = UblDateTime(lexical)

    assert str(value) == lexical
    assert value.fractional_digits == digits


def test_a_naive_value_stays_naive() -> None:
    """Inventing a timezone asserts an offset the document never stated, and the
    wrong guess moves the value to a different day."""
    value = UblDateTime("2026-08-05T23:30:00")

    assert value.has_timezone is False
    assert str(value) == "2026-08-05T23:30:00"


def test_a_zoned_value_reports_its_offset() -> None:
    value = UblDateTime("2026-08-05T10:00:00+02:00")

    assert value.has_timezone is True
    assert value.utc_offset == timedelta(hours=2)


# ── The instant is available without destroying the text ───────────────────


def test_the_parsed_instant_is_exposed_separately() -> None:
    value = UblDateTime("2026-08-05T10:00:00+02:00")

    assert value.to_datetime() == datetime(
        2026, 8, 5, 10, 0, tzinfo=timezone(timedelta(hours=2))
    )


def test_two_lexical_forms_of_one_instant_compare_equal_as_instants() -> None:
    """The point of keeping both: text comparison and instant comparison answer
    different questions, and both are legitimate."""
    zulu = UblDateTime("2026-08-05T10:00:00Z")
    offset = UblDateTime("2026-08-05T12:00:00+02:00")

    assert zulu.to_datetime() == offset.to_datetime()
    assert zulu != offset
    assert str(zulu) != str(offset)


def test_identical_lexical_forms_are_equal() -> None:
    assert UblDateTime("2026-08-05T10:00:00Z") == UblDateTime("2026-08-05T10:00:00Z")


def test_a_naive_value_has_no_instant_in_utc() -> None:
    """A naive value cannot be placed on the timeline without inventing an
    offset, so asking for one is refused rather than guessed."""
    value = UblDateTime("2026-08-05T10:00:00")

    with pytest.raises(UblValidationError):
        value.to_utc()


def test_a_zoned_value_converts_to_utc_on_request() -> None:
    """Explicit conversion is fine; it is silent conversion that is not."""
    value = UblDateTime("2026-08-05T12:00:00+02:00")

    assert value.to_utc() == datetime(2026, 8, 5, 10, 0, tzinfo=timezone.utc)


# ── Dates and times ────────────────────────────────────────────────────────


@pytest.mark.parametrize("lexical", ["2026-08-05", "2026-01-01", "2026-12-31"])
def test_a_date_round_trips_its_lexical_form(lexical: str) -> None:
    assert str(UblDate(lexical)) == lexical


def test_a_date_exposes_its_parsed_value() -> None:
    assert UblDate("2026-08-05").to_date() == date(2026, 8, 5)


@pytest.mark.parametrize(
    "lexical", ["10:00:00", "10:00:00Z", "10:00:00.500+02:00", "23:59:59"]
)
def test_a_time_round_trips_its_lexical_form(lexical: str) -> None:
    assert str(UblTime(lexical)) == lexical


# ── Malformed input is refused, not coerced ────────────────────────────────


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "not a date",
        "2026-13-01",
        "2026-08-32",
        "05/08/2026",
        "2026-08-05T25:00:00Z",
        "2026-08-05 10:00:00",
        "2026-08-05T10:00:00+25:00",
    ],
)
def test_malformed_date_times_are_refused(bad: str) -> None:
    with pytest.raises(UblValidationError):
        UblDateTime(bad)


@pytest.mark.parametrize("bad", ["2026-08-05T10:00:00Z", "2026-8-5", "", "2026-02-30"])
def test_malformed_dates_are_refused(bad: str) -> None:
    """A dateTime is not a date: accepting one where the schema says xsd:date
    would let a time component through into a field that cannot hold it."""
    with pytest.raises(UblValidationError):
        UblDate(bad)


def test_a_well_formed_value_passes_the_same_validation() -> None:
    """Control for the rejection tests above: the validator must accept the
    ordinary case, or the rejections prove only that it rejects everything."""
    assert str(UblDateTime("2026-08-05T10:00:00Z")) == "2026-08-05T10:00:00Z"
    assert str(UblDate("2026-08-05")) == "2026-08-05"
    assert str(UblTime("10:00:00")) == "10:00:00"


# ── Immutability, as with the other value types ────────────────────────────


def test_temporal_values_are_immutable() -> None:
    value = UblDateTime("2026-08-05T10:00:00Z")

    with pytest.raises(Exception):
        value.lexical = "2026-01-01T00:00:00Z"  # type: ignore[misc]
