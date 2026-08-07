"""NRRD-HEADER-001 -- "Accept the specification's permitted line endings
and lexical variants while preserving original lexical form in lossless
mode."

MUST (SAL-NRRD-OBL-6F9641D043F9DAAA, partial): "Permitted lexical variants
are not fully modeled or tested" was this obligation's own named gap.

Grounded directly in the pinned NRRD specification text
(.local/format-contracts/acquired/nrrd/src-nrrd-001.bin): "Field
specifications with alternate equivalent forms are listed together (for
example, 'block size' is the same as 'blocksize')." Programmatically
extracted every "<spaced>: <...> <unspaced>: <...>" adjacency in the spec
text where unspaced == spaced.replace(' ', ''), rather than transcribing
by hand, and cross-checked the result against the existing codebase:

    block size / blocksize   -- NOT previously recognized (fixed here)
    old min / oldmin         -- already handled (model/document.py)
    old max / oldmax         -- already handled (model/document.py)
    data file / datafile     -- NOT previously recognized (fixed here)
    line skip / lineskip     -- already handled (codec/reader/reader.py)
    byte skip / byteskip     -- already handled (codec/reader/reader.py)
    sample units / sampleunits -- already handled (model/document.py)

Five of the seven pairs were already correctly handled via a scattered
`header.get(canonical, header.get(alias))` fallback at each consumer, with
existing test coverage elsewhere in this suite (not re-tested here). This
file closes the two genuinely unhandled pairs directly: neither "blocksize"
nor "datafile" (unspaced) was recognized anywhere in the reader before this
slice -- confirmed by direct probing before any fix was written. Both are
now normalized to their canonical spaced key once, at parse time, in
_parse_header, rather than patched at every consumer -- "data file"
specifically because its own list-mode detection is itself keyed on the
exact parsed field name, so patching individual consumers could not have
fixed the LIST-detection path at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import NrrdParseError, load, loads


def _header(*fields: str) -> bytes:
    return ("NRRD0004\n" + "\n".join(fields) + "\n\n").encode()


def test_the_unspaced_blocksize_alias_is_recognized_for_a_block_typed_document() -> None:
    payload = _header(
        "type: block",
        "dimension: 1",
        "sizes: 1",
        "blocksize: 4",
        "encoding: raw",
    ) + bytes(4)

    document = loads(payload)

    assert document.header.get("block size") == "4"
    assert "blocksize" not in document.header


def test_the_unspaced_datafile_alias_is_recognized_and_resolves_the_detached_payload(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([9, 9, 9, 9]))
    header_path = tmp_path / "aliased.nhdr"
    header_path.write_bytes(
        _header(
            "type: uchar",
            "dimension: 1",
            "sizes: 4",
            "encoding: raw",
            "datafile: a.raw",
        )
    )

    document = load(header_path)

    assert document.array == [9, 9, 9, 9]
    assert document.header.get("data file") == "a.raw"
    assert "datafile" not in document.header


def test_declaring_both_the_spaced_and_unspaced_block_size_form_is_a_duplicate_field() -> None:
    payload = _header(
        "type: block",
        "dimension: 1",
        "sizes: 1",
        "block size: 4",
        "blocksize: 4",
        "encoding: raw",
    ) + bytes(4)

    with pytest.raises(NrrdParseError, match="duplicate"):
        loads(payload)


def test_declaring_both_the_spaced_and_unspaced_data_file_form_is_a_duplicate_field(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.raw").write_bytes(bytes([1, 2, 3, 4]))
    header_path = tmp_path / "duplicate.nhdr"
    header_path.write_bytes(
        _header(
            "type: uchar",
            "dimension: 1",
            "sizes: 4",
            "encoding: raw",
            "data file: a.raw",
            "datafile: a.raw",
        )
    )

    with pytest.raises(NrrdParseError, match="duplicate"):
        load(header_path)


def test_the_canonical_spaced_forms_still_parse_correctly_unaffected_by_the_alias_map() -> None:
    payload = _header(
        "type: block",
        "dimension: 1",
        "sizes: 1",
        "block size: 4",
        "encoding: raw",
    ) + bytes(4)

    document = loads(payload)

    assert document.header.get("block size") == "4"
