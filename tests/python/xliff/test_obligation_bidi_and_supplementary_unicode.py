"""XLIFF-VALIDATE-001 -- "Build validation matrices covering every core
structural and inline element plus each optional module, including
deeply nested and overlapping markers, paired-code errors, bidi content,
and supplementary Unicode code points."

MUST (SAL-XLIFF-OBL-BF7C86F8AFED34D6): nested/overlapping markers,
paired-code errors, and per-module coverage are all already proven
elsewhere (test_obligation_paired_code_integrity.py,
test_obligation_nested_group_hierarchy.py,
test_obligation_isolated_pairing_attribute_matching.py, the module-
coverage test files). "Bidi content" and "supplementary Unicode code
points" were the two genuinely untested items -- confirmed by grep
finding zero mentions of "bidi" or "supplementary" anywhere in the
existing suite before this slice.

This package's text pipeline is Python-string-native throughout (no
custom byte-level text handling), and ElementTree's own XML
serialization is UTF-8 by default -- there is no obvious mechanism by
which either bidi control characters or non-BMP (supplementary-plane)
code points would be mishandled. Confirmed directly by interactive probe
before writing these tests: both round-trip correctly through load and a
full dumps/reload cycle. These tests exist to make that verified, not
merely assumed.
"""

from __future__ import annotations

from format_factory.xliff import dumps, loads

_NS = "urn:oasis:names:tc:xliff:document:2.0"

_RLE = "‫"  # RIGHT-TO-LEFT EMBEDDING
_PDF = "‬"  # POP DIRECTIONAL FORMATTING
_ARABIC_HELLO = "مرحبا"  # "marhaba" in Arabic script
_EMOJI = "\U0001f600"  # GRINNING FACE, outside the Basic Multilingual Plane


def _document(source_text: str) -> bytes:
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">'
        f'<file id="f1"><unit id="u1"><segment id="s1">'
        f"<source>{source_text}</source>"
        f"</segment></unit></file></xliff>"
    ).encode("utf-8")


def _source_text(document) -> str:
    unit = next(document.iter_units())
    return "".join(item for item in unit.segments[0].source if isinstance(item, str))


def test_bidi_control_characters_survive_load() -> None:
    bidi_text = f"{_RLE}{_ARABIC_HELLO}{_PDF} world"

    document = loads(_document(bidi_text))

    assert _source_text(document) == bidi_text


def test_bidi_control_characters_survive_a_write_reload_round_trip() -> None:
    bidi_text = f"{_RLE}{_ARABIC_HELLO}{_PDF} world"

    document = loads(_document(bidi_text))
    reloaded = loads(dumps(document).encode("utf-8"))

    assert _source_text(reloaded) == bidi_text


def test_a_supplementary_plane_code_point_survives_load() -> None:
    text = f"before {_EMOJI} after"

    document = loads(_document(text))

    assert _source_text(document) == text
    assert len(_EMOJI) == 1, "a single Unicode code point, even though outside the BMP"


def test_a_supplementary_plane_code_point_survives_a_write_reload_round_trip() -> None:
    text = f"before {_EMOJI} after"

    document = loads(_document(text))
    reloaded = loads(dumps(document).encode("utf-8"))

    assert _source_text(reloaded) == text


def test_bidi_and_supplementary_code_points_coexist_in_one_segment() -> None:
    mixed = f"{_RLE}{_ARABIC_HELLO}{_PDF} {_EMOJI} plain text"

    document = loads(_document(mixed))
    reloaded = loads(dumps(document).encode("utf-8"))

    assert _source_text(document) == mixed
    assert _source_text(reloaded) == mixed
