"""ORA-VALIDATE-001 against the shipped namespace.

MUST: "Validate each layer independently, aggregate stable diagnostics,
distinguish errors from interoperability warnings, and never repair or
normalize unless explicitly requested."

Before this slice: "distinguish errors from interoperability warnings" was
unproven -- every Diagnostic this package emitted used Severity.ERROR, and
Severity.WARNING (already supported by the shared Diagnostic/Severity type)
was never constructed anywhere. validate() had no finding this package
would honestly classify as a non-fatal interoperability concern rather than
a hard error.

This file closes that gap with a genuine one: a document whose declared
version is older than what its own features require (load()'s existing
declared_version/detected_version machinery already computes this drift,
but validate() never surfaced it). Such a document is not invalid --
this reader parses it correctly regardless -- but a stricter reader that
honors only the declared version might reject or misinterpret it. That is
exactly an interoperability warning: reported at Severity.WARNING, which
ValidationReport.is_valid deliberately does not count against validity.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

from format_factory.core import Severity
from format_factory.ora import validate

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + chunk(b"IEND", b"")
    )


def _archive(stack_xml: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png(16, 16))
        zf.writestr("mergedimage.png", _png())
        zf.writestr("data/only.png", _png())
    return buffer.getvalue()


def _stack(version: str, *, isolated: bool = True) -> bytes:
    isolation = ' isolation="isolate"' if isolated else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<image w="8" h="8" version="{version}">'
        f"<stack><stack name=\"group\"{isolation}>"
        f'<layer name="only" src="data/only.png"/>'
        f"</stack></stack></image>"
    ).encode()


def test_a_document_declaring_an_older_version_than_it_uses_gets_a_warning() -> None:
    report = validate(_archive(_stack("0.0.1")))

    warnings = [d for d in report.diagnostics if d.severity == Severity.WARNING]
    assert len(warnings) == 1
    assert warnings[0].code == "ORA_DECLARED_VERSION_BELOW_DETECTED"
    assert "0.0.1" in warnings[0].message
    assert "0.0.4" in warnings[0].message


def test_the_warning_does_not_make_the_report_invalid() -> None:
    """The core distinction this obligation asks for: a warning is not an
    error. ValidationReport.is_valid excludes WARNING by design."""
    report = validate(_archive(_stack("0.0.1")))

    assert report.is_valid is True
    assert report.errors == ()


def test_no_warning_when_the_declared_version_already_matches() -> None:
    report = validate(_archive(_stack("0.0.4")))

    assert report.diagnostics == ()


def test_no_warning_when_the_declared_version_is_ahead_of_what_is_used() -> None:
    """A document may declare a newer profile than it happens to use --
    that is not drift in the direction this obligation warns about."""
    report = validate(_archive(_stack("0.0.5", isolated=False)))

    assert report.diagnostics == ()


def test_an_unparseable_declared_version_produces_no_warning_not_a_crash() -> None:
    """version has no format constraint in the specification's own grammar.
    Drift can only be judged between two comparable values -- an
    unparseable declared version means 'cannot determine', not 'assume the
    worst', and must never raise."""
    report = validate(_archive(_stack("not-a-version")))

    assert report.diagnostics == ()
    assert report.is_valid is True


def test_the_warning_coexists_with_a_real_error_and_both_are_reported() -> None:
    """Aggregation still holds: a version-drift warning and a genuine
    baseline-asset error surface in the same report, distinguishable by
    severity."""
    buffer = io.BytesIO()
    stack_xml = _stack("0.0.1")
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        # Thumbnail deliberately omitted -> a genuine ERROR alongside the WARNING.
        zf.writestr("mergedimage.png", _png())
        zf.writestr("data/only.png", _png())

    report = validate(buffer.getvalue())

    severities = {d.severity for d in report.diagnostics}
    assert Severity.WARNING in severities
    assert Severity.ERROR in severities
    assert report.is_valid is False
