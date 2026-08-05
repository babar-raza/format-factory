"""UBL temporal values: lexical form and timezone preserved verbatim.

  "Preserve timezone and lexical precision of date/time values"

The obvious implementation — parse to `datetime`, keep that, format it back on
write — destroys information the document asserted:

* `Z` and `+00:00` are the same instant and different lexical forms. A document
  that said `Z` and comes back saying `+00:00` has been modified.
* `10:00:00`, `10:00:00.0` and `10:00:00.000` are one instant with three
  declared precisions; trailing zeros are a precision claim, not noise.
* A naive value carries no offset. Inventing one asserts something the document
  never said, and the wrong guess moves the value to a different day.

So these types store the original text verbatim and *parse alongside it* rather
than reconstructing text from the parse. `str()` returns exactly what was read;
`to_datetime()` gives the instant when a caller genuinely wants arithmetic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from ..errors import UblValidationError

# XSD lexical shapes. These are deliberately stricter than
# `datetime.fromisoformat`, which accepts forms XSD does not (a space instead of
# `T`, single-digit months) and would silently admit a value the schema rejects.
_DATE = re.compile(r"^-?\d{4}-\d{2}-\d{2}$")
_TIMEZONE = r"(?:Z|[+-]\d{2}:\d{2})?"
_TIME = re.compile(rf"^\d{{2}}:\d{{2}}:\d{{2}}(\.\d+)?{_TIMEZONE}$")
_DATETIME = re.compile(rf"^-?\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}(\.\d+)?{_TIMEZONE}$")


def _parse_offset(lexical: str) -> timezone | None:
    if lexical.endswith("Z"):
        return timezone.utc
    match = re.search(r"([+-])(\d{2}):(\d{2})$", lexical)
    if match is None:
        return None
    sign, hours, minutes = match.group(1), int(match.group(2)), int(match.group(3))
    if hours > 23 or minutes > 59:
        raise UblValidationError(f"timezone offset out of range in {lexical!r}")
    delta = timedelta(hours=hours, minutes=minutes)
    return timezone(-delta if sign == "-" else delta)


def _fractional_digits(lexical: str) -> int:
    match = re.search(r"\.(\d+)", lexical)
    return len(match.group(1)) if match else 0


def _for_fromisoformat(lexical: str) -> str:
    """`Z` is not accepted by `fromisoformat` before 3.11 and is normalised by
    it after; substituting here keeps the original text untouched."""
    return lexical[:-1] + "+00:00" if lexical.endswith("Z") else lexical


@dataclass(frozen=True)
class UblDateTime:
    """An `xsd:dateTime` value. `str()` returns the original text exactly."""

    lexical: str

    def __post_init__(self) -> None:
        if not isinstance(self.lexical, str) or not _DATETIME.match(self.lexical):
            raise UblValidationError(
                f"{self.lexical!r} is not a well-formed xsd:dateTime "
                "(expected YYYY-MM-DDThh:mm:ss with optional fraction and timezone)"
            )
        try:
            datetime.fromisoformat(_for_fromisoformat(self.lexical))
        except ValueError as exc:
            raise UblValidationError(
                f"{self.lexical!r} is not a valid dateTime: {exc}"
            ) from exc
        _parse_offset(self.lexical)

    def __str__(self) -> str:
        return self.lexical

    @property
    def has_timezone(self) -> bool:
        return _parse_offset(self.lexical) is not None

    @property
    def utc_offset(self) -> timedelta | None:
        offset = _parse_offset(self.lexical)
        return offset.utcoffset(None) if offset is not None else None

    @property
    def fractional_digits(self) -> int:
        """Digits the document declared, including trailing zeros."""
        return _fractional_digits(self.lexical)

    def to_datetime(self) -> datetime:
        """The parsed instant, offset intact. Naive stays naive."""
        return datetime.fromisoformat(_for_fromisoformat(self.lexical))

    def to_utc(self) -> datetime:
        """Convert to UTC. Refuses a naive value rather than assuming one."""
        if not self.has_timezone:
            raise UblValidationError(
                f"{self.lexical!r} carries no timezone, so it cannot be placed on "
                "the timeline without inventing an offset the document never stated"
            )
        return self.to_datetime().astimezone(timezone.utc)


@dataclass(frozen=True)
class UblDate:
    """An `xsd:date` value."""

    lexical: str

    def __post_init__(self) -> None:
        if not isinstance(self.lexical, str) or not _DATE.match(self.lexical):
            raise UblValidationError(
                f"{self.lexical!r} is not a well-formed xsd:date (expected "
                "YYYY-MM-DD). A dateTime is a different type and is not accepted "
                "here, because a time component cannot be held by a date field."
            )
        try:
            date.fromisoformat(self.lexical)
        except ValueError as exc:
            raise UblValidationError(f"{self.lexical!r} is not a valid date: {exc}") from exc

    def __str__(self) -> str:
        return self.lexical

    def to_date(self) -> date:
        return date.fromisoformat(self.lexical)


@dataclass(frozen=True)
class UblTime:
    """An `xsd:time` value."""

    lexical: str

    def __post_init__(self) -> None:
        if not isinstance(self.lexical, str) or not _TIME.match(self.lexical):
            raise UblValidationError(
                f"{self.lexical!r} is not a well-formed xsd:time "
                "(expected hh:mm:ss with optional fraction and timezone)"
            )
        try:
            time.fromisoformat(_for_fromisoformat(self.lexical))
        except ValueError as exc:
            raise UblValidationError(f"{self.lexical!r} is not a valid time: {exc}") from exc
        _parse_offset(self.lexical)

    def __str__(self) -> str:
        return self.lexical

    @property
    def has_timezone(self) -> bool:
        return _parse_offset(self.lexical) is not None

    @property
    def fractional_digits(self) -> int:
        return _fractional_digits(self.lexical)

    def to_time(self) -> time:
        return time.fromisoformat(_for_fromisoformat(self.lexical))


__all__ = ["UblDate", "UblDateTime", "UblTime"]
