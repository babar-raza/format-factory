"""NRRD-META-001 -- baseline basic metadata: content, min, max, old min,
old max, and number.

MUST (SAL-NRRD-OBL-1FE17FFCC0572ABC): "Preserve baseline optional basic
and per-axis metadata with absence-vs-explicit-value distinctions and the
format's quoting/escaping rules; carry obsolete number and range fields in
lossless mode."

MUST (SAL-NRRD-OBL-556FAEE08EA61D1A; Teem NRRD Format Specification
Section 5): "Baseline basic metadata includes content, min, max, old min,
old max, and number fields with the optionality, numeric meaning, and
legacy-preservation behavior defined by the specification."

Before this slice: none of content/min/max/old min/old max/number had a
typed accessor anywhere in the model -- confirmed by grepping document.py
directly. Every field's exact semantics were read from the pinned spec
source rather than guessed: `content` is an unquoted free-text string with
no explicit delimiting; `min`/`max` are doubles where any value including
infinite or NaN is legal; `old min`/`old max` are doubles "meaningless for
floating-point and block nrrds," recording a linear-quantization input
range, each with an unspaced alias spelling (`oldmin`/`oldmax`); `number`
is an obsolete, vestigial field the spec explicitly instructs readers to
"always ignore... without even an attempt to parse the field as an
integer" -- exposed here as raw text only, never parsed as a number,
matching that instruction exactly rather than inventing int-parsing the
spec explicitly forbids.
"""

from __future__ import annotations

import math

from format_factory.nrrd import dumps, loads


def _header(extra: str = "") -> bytes:
    fields = "NRRD0005\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
    if extra:
        fields += extra + "\n"
    return (fields + "\n").encode() + b"\x00\x00"


def test_content_projects_as_a_plain_unquoted_string() -> None:
    document = loads(_header("content: a test volume"))

    assert document.content == "a test volume"


def test_min_and_max_project_as_doubles() -> None:
    document = loads(_header("min: -1.5\nmax: 2.5"))

    assert document.min_value == -1.5
    assert document.max_value == 2.5


def test_min_accepts_nan_and_max_accepts_infinite() -> None:
    """The spec permits "any value, infinite or not, NaN or not" for min
    and max."""
    document = loads(_header("min: nan\nmax: inf"))

    assert math.isnan(document.min_value)
    assert math.isinf(document.max_value)


def test_old_min_and_old_max_project_as_doubles() -> None:
    document = loads(_header("old min: 0\nold max: 255"))

    assert document.old_min == 0.0
    assert document.old_max == 255.0


def test_old_min_and_old_max_unspaced_aliases_also_project() -> None:
    document = loads(_header("oldmin: 1\noldmax: 254"))

    assert document.old_min == 1.0
    assert document.old_max == 254.0


def test_number_is_exposed_as_raw_text_never_parsed() -> None:
    """The spec's own explicit instruction: "the number field should never
    be written, and always ignored on reading, without even an attempt to
    parse the field as an integer." -- proven here with a value that is
    not even a valid integer, confirming no parsing is ever attempted."""
    document = loads(_header("number: not-a-number-at-all"))

    assert document.number == "not-a-number-at-all"


def test_all_six_baseline_fields_are_none_when_absent() -> None:
    document = loads(_header())

    assert document.content is None
    assert document.min_value is None
    assert document.max_value is None
    assert document.old_min is None
    assert document.old_max is None
    assert document.number is None


def test_baseline_metadata_requires_no_version_beyond_nrrd0001() -> None:
    """Unlike thicknesses/sample_units (NRRD0004+), these are baseline
    fields with no version gate."""
    document = loads(
        (
            "NRRD0001\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
            "content: baseline\nmin: 0\nnumber: 2\n\n"
        ).encode()
        + b"\x00\x00"
    )

    assert document.content == "baseline"
    assert document.min_value == 0.0
    assert document.minimal_version_for() == 1


def test_baseline_metadata_survives_a_round_trip() -> None:
    document = loads(
        _header("content: a test volume\nmin: -1.5\nmax: 2.5\nold min: 0\nold max: 255\nnumber: 2")
    )

    reloaded = loads(dumps(document))

    assert reloaded.content == "a test volume"
    assert reloaded.min_value == -1.5
    assert reloaded.max_value == 2.5
    assert reloaded.old_min == 0.0
    assert reloaded.old_max == 255.0
    assert reloaded.number == "2"
