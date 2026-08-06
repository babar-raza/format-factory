"""UBL-LIFECYCLE-001 -- strict vs. preservation read-mode behavior.

MUST (SAL-UBL-OBL-6C91BBF7F11E4402): "Support a strict read mode that
rejects malformed input with diagnostics and a tolerant read mode that
recovers where the format permits, with recovery actions reported."

Before this slice, mode="strict"/"preservation" was validated as one of two
accepted strings in loads()/load(), but no test ever passed mode="preservation"
explicitly, and reader.py never branches on the mode value for malformed-input
handling -- both modes currently reject a given malformed document identically.
The obligation's "tolerant read mode that recovers ... with recovery actions
reported" is not implemented: there is no recovery-action report type, and no
document that "preservation" mode accepts while "strict" rejects.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblParseError, loads

_MALFORMED = b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><bad'


def test_strict_mode_rejects_malformed_xml_with_a_diagnostic() -> None:
    with pytest.raises(UblParseError, match="malformed XML"):
        loads(_MALFORMED, mode="strict")


def test_preservation_mode_currently_rejects_the_same_malformed_xml_identically() -> None:
    """Characterizes the current (honest) state: 'preservation' is accepted as
    a mode value but provides no distinct fault-tolerant recovery path yet --
    both modes reject this malformed document the same way."""

    with pytest.raises(UblParseError, match="malformed XML"):
        loads(_MALFORMED, mode="preservation")


def test_an_unrecognized_mode_string_is_rejected() -> None:
    with pytest.raises(ValueError, match="mode must be"):
        loads(_MALFORMED, mode="tolerant")
