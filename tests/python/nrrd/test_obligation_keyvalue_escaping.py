"""NRRD-KEYVALUE-001 -- key/value backslash-escaping and the NRRD0002
version gate.

MUST (SAL-NRRD-OBL-48CB227B444651BA / SAL-NRRD-OBL-6533C8FB0044E3A2, Teem
NRRD Format Specification Sections 1.1 and 1.2): "key:=value pairs ... with
defined newline and backslash escaping ... Starting with NRRD0002."

The pinned spec source (src-nrrd-001.bin) states the escaping scheme
precisely: "a minimal escaping scheme is required, which readers must
interpret and writers must generate: '\\n' signifies a new line, as defined
by the '\\n' character constant in C; '\\\\' signifies the backslash
character, the '\\\\' character constant in C" and "These can appear in
NRRD0002 (and higher version) files, but not NRRD0001 files."

Before this slice: neither reader.py nor writer.py implemented this
escaping at all -- key/value values were stored and emitted raw. A value
containing a real newline or backslash character (e.g. a Windows path, or
free-text notes with embedded line breaks) produced a header that could not
be parsed back -- dumps() followed by loads() raised NrrdParseError,
confirmed interactively before this fix. There was also no NRRD0002 version
gate: a NRRD0001 header carrying a key:=value line was silently accepted,
contradicting the spec's explicit statement that key/value pairs did not
exist before NRRD0002.
"""

from __future__ import annotations

import dataclasses

import pytest

from format_factory.nrrd import dumps, loads
from format_factory.nrrd.errors import NrrdParseError


def _document(*, version: int = 5) -> bytes:
    return (
        f"NRRD000{version}\n"
        "type: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n\n\x00\x00"
    ).encode()


def test_an_embedded_newline_round_trips_through_dumps_and_loads() -> None:
    original = loads(_document())
    original = dataclasses.replace(
        original, key_value_pairs={"note": "line one\nline two"}
    )

    reloaded = loads(dumps(original))

    assert reloaded.key_value_pairs == {"note": "line one\nline two"}


def test_an_embedded_backslash_round_trips_through_dumps_and_loads() -> None:
    original = loads(_document())
    original = dataclasses.replace(
        original, key_value_pairs={"path": r"C:\Users\x"}
    )

    reloaded = loads(dumps(original))

    assert reloaded.key_value_pairs == {"path": r"C:\Users\x"}


def test_the_written_header_escapes_backslash_before_newline() -> None:
    """Escaping order matters: a literal backslash must become "\\\\" (not
    be mistaken for the start of a "\\n" sequence) before any newline
    escaping is applied."""
    original = loads(_document())
    original = dataclasses.replace(original, key_value_pairs={"k": "a\\nb"})

    reloaded = loads(dumps(original))

    assert reloaded.key_value_pairs == {"k": "a\\nb"}


def test_a_raw_backslash_n_escape_sequence_decodes_to_a_real_newline() -> None:
    document = loads(_document()[:-3] + b"note:=line1\\nline2\n\n\x00\x00")

    assert document.key_value_pairs == {"note": "line1\nline2"}


def test_a_raw_double_backslash_decodes_to_one_backslash() -> None:
    document = loads(_document()[:-3] + b"path:=C:\\\\Users\n\n\x00\x00")

    assert document.key_value_pairs == {"path": "C:\\Users"}


@pytest.mark.parametrize("version", [1])
def test_key_value_pairs_are_rejected_before_nrrd0002(version: int) -> None:
    source = _document(version=version)[:-3] + b"foo:=bar\n\n\x00\x00"

    with pytest.raises(NrrdParseError):
        loads(source)


@pytest.mark.parametrize("version", [2, 3, 4, 5])
def test_key_value_pairs_are_accepted_from_nrrd0002_onward(version: int) -> None:
    source = _document(version=version)[:-3] + b"foo:=bar\n\n\x00\x00"

    document = loads(source)

    assert document.key_value_pairs == {"foo": "bar"}
