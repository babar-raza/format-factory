"""NRRD-HEADER-001 -- "Recognize every specified magic/version; parse
ordinary fields and comments; enforce field uniqueness/ordering;
preserve unknown metadata and optional-field absence."

MUST (SAL-NRRD-OBL-7D1A84A3077B90C2, partial): magic/version recognition,
ordinary field/comment parsing, field uniqueness, unknown-metadata and
optional-field-absence preservation were already directly tested. Field
ordering was the one remaining, named gap in this obligation's own
missing_behavior.

Grounded directly in the pinned NRRD specification text
(.local/format-contracts/acquired/nrrd/src-nrrd-001.bin): "the only
constraint on field specification ordering is that the 'data file: LIST'
form of the data file field ... must be the last field specification in
the header. Within these constraints, the field specification may appear
in any order." This is the ONLY ordering rule the format defines -- no
other field has a positional requirement.

Before this slice: nothing in reader.py explicitly rejects a field
specification placed after "data file: LIST". Investigation (direct
source read of _parse_header's list_mode handling) showed the reader
already enforces this correctly, but by construction rather than by an
explicit check: once "data file: LIST" is seen, every subsequent
non-blank line unconditionally becomes a list-file entry, so a
would-be field specification appearing after it is never recognized
as a field at all -- it is consumed as a (typically nonexistent)
filename instead, surfacing as a clear detached-payload read error
rather than being silently misparsed as the field it looks like. This
is the correct spec-compliant behavior (nothing can follow "data file:
LIST" as a field), but it had no test proving it before this slice.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import NrrdParseError, load


def _header(*fields: str) -> bytes:
    return ("NRRD0004\n" + "\n".join(fields) + "\n\n").encode()


def test_data_file_list_as_the_true_last_field_specification_reads_correctly(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.raw").write_bytes(b"\x01\x02")
    (tmp_path / "b.raw").write_bytes(b"\x03\x04")
    header_path = tmp_path / "ordered.nhdr"
    header_path.write_bytes(
        _header(
            "type: uchar",
            "dimension: 1",
            "sizes: 4",
            "encoding: raw",
            "data file: LIST",
            "a.raw",
            "b.raw",
        )
    )

    document = load(header_path)

    assert document.array == [1, 2, 3, 4]


def test_a_field_looking_line_after_data_file_list_is_never_parsed_as_a_field(
    tmp_path: Path,
) -> None:
    """A line shaped exactly like a real field specification ("encoding:
    gzip") placed after "data file: LIST" must not be recognized as that
    field -- the spec allows nothing to follow "data file: LIST" as a
    field, so this line can only ever be interpreted as a list-file name.
    Proven by observing it fails as a missing file, not as a silently
    accepted (and wrong) encoding override."""
    (tmp_path / "a.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "misplaced.nhdr"
    header_path.write_bytes(
        _header(
            "type: uchar",
            "dimension: 1",
            "sizes: 2",
            "encoding: raw",
            "data file: LIST",
            "a.raw",
            "encoding: gzip",
        )
    )

    with pytest.raises(NrrdParseError, match="cannot read detached payload"):
        load(header_path)


def test_a_comment_looking_line_after_data_file_list_is_never_parsed_as_a_comment(
    tmp_path: Path,
) -> None:
    """Symmetric to the field case: a "#"-prefixed line after "data file:
    LIST" is likewise not treated as a comment -- it becomes a literal
    (nonexistent) filename beginning with "#", proving the list-mode
    switch is unconditional rather than selectively skipping comments."""
    (tmp_path / "a.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "comment-after-list.nhdr"
    header_path.write_bytes(
        _header(
            "type: uchar",
            "dimension: 1",
            "sizes: 2",
            "encoding: raw",
            "data file: LIST",
            "a.raw",
            "# not a real comment once inside a LIST block",
        )
    )

    with pytest.raises(NrrdParseError, match="cannot read detached payload"):
        load(header_path)
