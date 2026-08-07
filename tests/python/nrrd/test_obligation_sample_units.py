"""NRRD-PHYSICALMETA-001 -- the `sample units` field, distinct from
per-axis `units`, `space units`, and `thicknesses`.

MUST (SAL-NRRD-OBL-00F18A8DA59864CD): "Model thicknesses and sample units
only for NRRD0004 and newer; keep thickness distinct from spacing and
sample units distinct from axis and space units."

MUST (SAL-NRRD-OBL-38F3D4743DF2B0F9; Teem NRRD Format Specification
Sections 1.1, 5, and 6): "Starting with NRRD0004, thicknesses provides one
optional thickness per array axis and sample units provides a single
quoted unit for the values stored in the array."

The pinned spec source (src-nrrd-001.bin) states this precisely: "sample
units: <string>" / "sampleunits: <string>" -- "Always optional. This
provides a way of storing the units of measurement associated with the
scalar values stored in the array itself... Note that these units
describe the individual scalar values, and not some non-scalar value
stored along an axis of the array." Unlike the obligation's own paraphrase
("a single quoted unit"), the spec's own worked example ("sample units:
PPM") is unquoted plain text, not the `"..."`-delimited per-axis syntax
`labels`/`units` use -- confirmed directly against the pinned source
rather than trusting the paraphrase.

Before this slice: no `sample_units` accessor existed anywhere in the
model, and the field was not version-gated at all (a document declaring
`sample units` with an NRRD0001-0003 magic would not be flagged as
needing NRRD0004+).
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdDocument, dumps, loads
from format_factory.nrrd.errors import NrrdWriteError


def _header(*, version: int = 5, extra: str = "") -> bytes:
    fields = f"NRRD000{version}\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
    if extra:
        fields += f"{extra}\n"
    return (fields + "\n").encode() + b"\x00\x00"


def test_sample_units_projects_from_the_spaced_field_name() -> None:
    document = loads(_header(extra="sample units: PPM"))

    assert document.sample_units == "PPM"


def test_sample_units_projects_from_the_unspaced_alias() -> None:
    document = loads(_header(extra="sampleunits: parts-per-million"))

    assert document.sample_units == "parts-per-million"


def test_sample_units_is_none_when_absent() -> None:
    document = loads(_header())

    assert document.sample_units is None


def test_sample_units_is_unquoted_plain_text_not_a_per_axis_quoted_list() -> None:
    """Distinct from `units`/`labels`, which use "..."-delimited per-axis
    syntax -- the spec's own worked example ("sample units: PPM") carries
    no quotes at all."""
    document = loads(_header(extra="sample units: parts per million"))

    assert document.sample_units == "parts per million"


def test_sample_units_survives_a_round_trip() -> None:
    document = loads(_header(extra="sample units: PPM"))

    reloaded = loads(dumps(document))

    assert reloaded.sample_units == "PPM"


def test_sample_units_is_distinct_from_axis_units_and_space_units() -> None:
    document = NrrdDocument(
        version=5,
        header={
            "type": "uint8",
            "dimension": "1",
            "sizes": "2",
            "encoding": "raw",
            "units": '"mm"',
            "sample units": "PPM",
        },
        payload=b"\x00\x00",
        array=[0, 0],
    )

    assert document.units == ["mm"]
    assert document.sample_units == "PPM"


def test_sample_units_requires_nrrd0004_or_newer_when_writing() -> None:
    document = loads(_header(extra="sample units: PPM"))

    with pytest.raises(NrrdWriteError, match="sample units"):
        dumps(document, profile="NRRD0003")
