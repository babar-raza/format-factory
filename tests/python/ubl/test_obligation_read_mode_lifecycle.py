"""UBL-LIFECYCLE-001 -- strict vs. preservation read-mode behavior.

MUST (SAL-UBL-OBL-6C91BBF7F11E4402): "Support a strict read mode that
rejects malformed input with diagnostics and a tolerant read mode that
recovers where the format permits, with recovery actions reported."

This file characterizes the boundary of what tolerant mode does NOT
recover: malformed XML syntax (ElementTree cannot produce a tree to
recover into at all) stays a hard failure under both modes, matching the
same discipline test_obligation_tolerant_recovery_mode.py proves for the
one defect this reader's own structure makes genuinely recoverable (a
root namespace mismatch) -- see that file for the actual recovery path
and the reader.py::recovery_actions field it now proves.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblParseError, loads

_MALFORMED = b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><bad'


def test_strict_mode_rejects_malformed_xml_with_a_diagnostic() -> None:
    with pytest.raises(UblParseError, match="malformed XML"):
        loads(_MALFORMED, mode="strict")


def test_preservation_mode_still_rejects_genuinely_malformed_xml() -> None:
    """Malformed XML syntax is genuinely unrecoverable -- there is no tree
    to recover into at all -- so both modes reject it identically, unlike
    the root-namespace-mismatch case tolerant mode does recover from."""

    with pytest.raises(UblParseError, match="malformed XML"):
        loads(_MALFORMED, mode="preservation")


def test_an_unrecognized_mode_string_is_rejected() -> None:
    with pytest.raises(ValueError, match="mode must be"):
        loads(_MALFORMED, mode="tolerant")
