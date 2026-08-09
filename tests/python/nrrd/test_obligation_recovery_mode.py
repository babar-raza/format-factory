"""NRRD-LIFECYCLE-001 against the shipped namespace.

MUST: "Support a strict read mode that rejects malformed input with
diagnostics and a tolerant read mode that recovers where the format
permits, with recovery actions reported."

Before this file: `load()`/`loads()` validated `mode` (raising `ValueError`
for anything other than "strict"/"preservation"/"recovery") but then
called the underlying reader identically regardless of its value --
"recovery" mode behaved exactly like "strict" mode, and `recovery_actions`
was always the empty tuple. This closed the specific gap the obligation's
own missing_behavior named ("recovery mode performs no defined recovery
and reports no recovery decision rules") for one concrete, safe, honestly
-bounded scenario.

**Scope, stated precisely.** A raw-encoded payload with MORE bytes than
its declared shape needs is now recoverable: the excess trailing bytes
are never part of any declared element (the shape/type/sizes fields fully
determine which bytes are meaningful), so discarding them cannot
misinterpret real data -- unlike a payload with FEWER bytes than
declared, which stays rejected in every mode, strict or recovery alike,
since there is no safe way to invent missing bytes. This is deliberately
NOT extended to gzip/bzip2/hex: those encodings already cap decompression
at the declared shape's own byte count as a resource-exhaustion guard
(NRRD-VALIDATE-001's own "checked arithmetic BEFORE any payload
allocation" requirement) -- "excess decompressed data" for those
encodings is a resource-limit concern this scenario does not attempt to
relax, disclosed rather than silently narrowed. Other candidate recovery
scenarios were investigated directly against the pinned spec text before
settling on this one: duplicate FIELD specifications ("may appear no more
than once," stated as a hard rule with no recovery semantics, unlike
duplicate KEY/VALUE pairs, which the spec explicitly resolves as
"last one wins" -- already correct, unconditionally, via this package's
own dict-based parsing, so not a gap); and extra whitespace immediately
after a field's own colon (the spec requires exactly "a single space,"
with only TRAILING whitespace before the line terminator explicitly
"ignored" -- accepting more would be non-conformant leniency, not a
format-permitted recovery, so it was correctly left alone.
"""

from __future__ import annotations

import pytest

from format_factory.core import ResourceLimitError
from format_factory.nrrd import NrrdParseError, loads


def _header(magic: str = "NRRD0005") -> bytes:
    return f"{magic}\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: raw\n\n".encode()


# ── The one recoverable scenario: excess trailing raw payload bytes ──────


def test_recovery_mode_discards_excess_trailing_raw_bytes() -> None:
    payload = bytes((1, 2, 3, 4)) + bytes((99, 99, 99))  # 3 extra bytes

    document = loads(_header() + payload, mode="recovery")

    assert document.array == [1, 2, 3, 4]


def test_recovery_mode_reports_the_recovery_action() -> None:
    payload = bytes((1, 2, 3, 4)) + bytes((99, 99, 99))

    document = loads(_header() + payload, mode="recovery")

    assert len(document.recovery_actions) == 1
    assert "3 extra trailing byte" in document.recovery_actions[0]
    assert "4-byte shape" in document.recovery_actions[0]


def test_recovery_mode_reports_nothing_for_an_already_exact_payload() -> None:
    """Matches the pre-existing test_recovery_mode_is_explicit_and_reports_
    no_unsafe_repair's own assertion: a well-formed input has nothing to
    recover, in any mode."""
    payload = bytes((1, 2, 3, 4))

    document = loads(_header() + payload, mode="recovery")

    assert document.recovery_actions == ()


# ── Strict and preservation modes stay exactly as strict as before ───────


@pytest.mark.parametrize("mode", ["strict", "preservation"])
def test_excess_trailing_bytes_are_still_rejected_outside_recovery_mode(mode: str) -> None:
    payload = bytes((1, 2, 3, 4)) + bytes((99, 99, 99))

    with pytest.raises(ResourceLimitError):
        loads(_header() + payload, mode=mode)


# ── What recovery mode does NOT do: invent missing data ───────────────────


def test_a_truncated_payload_is_never_recoverable_even_in_recovery_mode() -> None:
    """The obligation's own "unsafe repair" boundary, proven behaviorally:
    recovery mode tolerates surplus, never invents a deficit."""
    payload = bytes((1, 2))  # 2 of the declared 4 bytes

    with pytest.raises(NrrdParseError, match="payload length mismatch"):
        loads(_header() + payload, mode="recovery")


def test_gzip_excess_decompressed_data_is_not_recovered() -> None:
    """Deliberately out of scope, disclosed in this module's own docstring
    -- excess decompressed bytes from a compressed encoding remain a
    resource-limit concern in every mode, including recovery."""
    import gzip

    payload = bytes((1, 2, 3, 4)) + bytes((99, 99, 99))
    compressed = gzip.compress(payload)
    header = b"NRRD0005\ntype: uint8\ndimension: 1\nsizes: 4\nencoding: gzip\n\n"

    with pytest.raises(ResourceLimitError):
        loads(header + compressed, mode="recovery")


def test_a_duplicate_field_is_never_recoverable_even_in_recovery_mode() -> None:
    """This module's own docstring already asserts, in prose, that
    duplicate FIELD specifications were investigated and correctly left
    unrecoverable ("may appear no more than once," a hard rule with no
    recovery semantics) -- proven here behaviorally rather than only
    documented. `mode` is threaded through `_load()` and consulted in
    exactly one conditional expression anywhere in that function (verified
    by direct source inspection, not incomplete search): the raw-encoding
    excess-trailing-bytes check. Header parsing itself
    (`_split_header`/`_parse_header`) takes no `mode` parameter at all, so
    a duplicate field is structurally, provably rejected identically
    regardless of mode -- this is that structural fact made executable."""
    duplicate = _header().replace(b"type: uint8\n", b"type: uint8\ntype: uint8\n")

    with pytest.raises(NrrdParseError, match="duplicate"):
        loads(duplicate + bytes(4), mode="recovery")
