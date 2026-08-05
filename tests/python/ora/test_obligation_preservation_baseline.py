"""ORA-PRESERVE-001 against the shipped namespace.

MUST: "Distinguish lossless round-trip output mode from normalized/
canonical output mode as an explicit caller choice." "Report every
construct that cannot be preserved before saving, through a loss report
API, rather than failing silently." "Preserve unknown or future-version
constructs that can be carried safely; never silently drop unrecognized
content in lossless mode." "Preserve the distinction between an absent
optional value and an explicitly written default or empty value."

required_tests: "Each preservation baseline behavior has a focused positive
test and, where refusable, a negative test proving refusal with
diagnostics."

Scope of this file:

* Obligation 1 (LOSSLESS vs CANONICAL as an explicit caller choice) and
  obligation 3 (unknown constructs survive a lossless round trip) were
  already implemented before this slice -- `lifecycle.PreservationMode` and
  `dumps()`'s member handling -- with zero tests framed under this
  obligation. Proven here with no source change.
* Obligation 2 (a loss report before saving) was genuinely absent: nothing
  told a caller, before choosing CANONICAL, which constructs regeneration
  would drop. Built as `preservation.check_preservation()` this slice.
* Obligation 4 (preserve absent-vs-explicit-default) is NOT attempted here
  and is NOT claimed anywhere in this file. `model/stack.py`'s `OraNode`
  applies attribute defaults at construction time by deliberate design
  ("a caller never has to distinguish 'absent' from 'explicitly default' to
  composite correctly" -- its own docstring), which is correct for
  compositing but means the in-memory model cannot currently answer "was
  opacity=1.0 written explicitly, or just defaulted?". Fixing that would
  need nullable defaults threaded through `OraNode`/`OraStack`/`OraLayer`
  and every consumer of them (`is_isolated_group` included) -- real,
  larger-scoped work, deferred rather than attempted partially here. The
  archive-level round trip is unaffected: LOSSLESS mode keeps the original
  bytes verbatim regardless of what the model captures.
"""

from __future__ import annotations

import io
import zipfile

from format_factory.ora import (
    LossReport,
    OraStack,
    PreservationMode,
    check_preservation,
    dumps,
    load,
)
from format_factory.ora.codec.container import STACK_MEMBER

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    import struct
    import zlib

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


_PLAIN_STACK_XML = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<image w="8" h="8" version="0.0.5">'
    b'<stack><layer name="only" src="data/only.png"/></stack></image>'
)

#: A stack element carrying an attribute no version of this library models --
#: the kind of vendor extension or future-profile field lossless mode exists
#: to survive.
_VENDOR_STACK_XML = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<image w="8" h="8" version="0.0.5">'
    b'<stack data-vendor-tag="acme-paint-v9">'
    b'<layer name="only" src="data/only.png" vendor-blend-mode="glow"/>'
    b"</stack></image>"
)


# ── Obligation 1: LOSSLESS vs CANONICAL as an explicit caller choice ───────


def test_preservation_mode_is_an_explicit_dumps_parameter() -> None:
    image = load(_archive(_PLAIN_STACK_XML))

    lossless = dumps(image, preservation=PreservationMode.LOSSLESS)
    canonical = dumps(image, preservation=PreservationMode.CANONICAL)

    assert lossless != canonical


def test_dumps_defaults_to_lossless_not_canonical() -> None:
    """"Defaulting to CANONICAL would silently discard [unmodeled content]
    on any load-then-save, which is the destructive option and the wrong
    default." (lifecycle.py's own module docstring.)"""
    image = load(_archive(_VENDOR_STACK_XML))

    default_output = dumps(image)
    explicit_lossless = dumps(image, preservation=PreservationMode.LOSSLESS)

    assert default_output == explicit_lossless


# ── Obligation 3: unknown constructs survive a lossless round trip ─────────


def test_lossless_round_trip_preserves_an_unmodeled_stack_attribute() -> None:
    image = load(_archive(_VENDOR_STACK_XML))

    output = dumps(image, preservation=PreservationMode.LOSSLESS)

    reloaded_members = zipfile.ZipFile(io.BytesIO(output))
    stack_bytes = reloaded_members.read(STACK_MEMBER)
    assert b'data-vendor-tag="acme-paint-v9"' in stack_bytes
    assert b'vendor-blend-mode="glow"' in stack_bytes


def test_canonical_round_trip_drops_the_unmodeled_attribute() -> None:
    """Control: proves the vendor attribute is genuinely unmodeled (CANONICAL
    regeneration cannot re-emit what the model never captured), not that the
    fixture is broken."""
    image = load(_archive(_VENDOR_STACK_XML))

    output = dumps(image, preservation=PreservationMode.CANONICAL)

    reloaded_members = zipfile.ZipFile(io.BytesIO(output))
    stack_bytes = reloaded_members.read(STACK_MEMBER)
    assert b"data-vendor-tag" not in stack_bytes
    assert b"vendor-blend-mode" not in stack_bytes


# ── Obligation 2: a loss report before saving ───────────────────────────────


def test_lossless_target_reports_no_loss() -> None:
    image = load(_archive(_VENDOR_STACK_XML))

    report = check_preservation(image, target=PreservationMode.LOSSLESS)

    assert isinstance(report, LossReport)
    assert report.is_lossless is True
    assert report.items == ()


def test_canonical_target_reports_the_unmodeled_stack_attribute() -> None:
    image = load(_archive(_VENDOR_STACK_XML))

    report = check_preservation(image, target=PreservationMode.CANONICAL)

    assert report.is_lossless is False
    attribute_names = {item.attribute for item in report.items}
    assert "data-vendor-tag" in attribute_names
    assert "vendor-blend-mode" in attribute_names


def test_loss_report_items_carry_element_and_value_for_diagnostics() -> None:
    image = load(_archive(_VENDOR_STACK_XML))

    report = check_preservation(image, target=PreservationMode.CANONICAL)

    by_attribute = {item.attribute: item for item in report.items}
    stack_loss = by_attribute["data-vendor-tag"]
    assert stack_loss.element == "stack"
    assert stack_loss.value == "acme-paint-v9"
    assert "data-vendor-tag" in stack_loss.message

    layer_loss = by_attribute["vendor-blend-mode"]
    assert layer_loss.element == "layer"
    assert layer_loss.value == "glow"


def test_canonical_target_reports_no_loss_for_a_document_with_only_modeled_attributes() -> None:
    """Positive control: a document using only spec-defined attributes loses
    nothing under CANONICAL regeneration either."""
    image = load(_archive(_PLAIN_STACK_XML))

    report = check_preservation(image, target=PreservationMode.CANONICAL)

    assert report.is_lossless is True
    assert report.items == ()


def test_loss_report_locates_a_deeply_nested_unmodeled_attribute() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack><stack name="group">'
        b'<layer name="only" src="data/only.png" vendor-x="1"/>'
        b"</stack></stack></image>"
    )
    image = load(_archive(stack_xml))

    report = check_preservation(image, target=PreservationMode.CANONICAL)

    (item,) = report.items
    assert item.attribute == "vendor-x"
    assert item.path[0] == "image[0]"
    assert any(segment.startswith("stack[") for segment in item.path)
