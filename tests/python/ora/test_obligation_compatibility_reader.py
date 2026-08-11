"""ORA-CONTAINER-001 / ORA-MIMETYPE-001 / ORA-DOCUMENT-001 — the
`ReadMode.TOLERANT` compatibility-reader extension (2026-08-11).

Workstream C (EP-3-routed): extends the pre-existing `ReadMode.TOLERANT`
mechanism to cover 2 real, independently-confirmed non-conformances found in
the vendored third-party GPL MyPaint corpus
(tests/python/ora/fixtures/third-party-gpl-mypaint/PROVENANCE.md):

1. `bigimage.ora` / `fill_outlines.ora` fail the mimetype-first-archive
   -member check (their real first ZIP member, by true central-directory
   order, is `data/` and `Thumbnails/` respectively).
2. `smallimage.ora` fails the required `version` attribute check on the
   root `<image>` element (its stack.xml has no version attribute at all).

This is a narrow, enumerated exception list, not a general relaxation:

- STRICT mode is unchanged -- every pre-existing strict-mode test in
  `test_obligation_container_and_mimetype.py` and
  `test_obligation_stack_and_document.py` still passes unmodified (see
  those files' own `test_mimetype_first_rule_correctly_rejects_a_real_
  independent_producers_archive` / `test_required_version_attribute_
  correctly_rejects_a_real_independent_producers_document`, added earlier
  this session against the same 3 files -- their assertions are untouched).
- TOLERANT mode still refuses everything it always refused: missing
  mimetype member entirely, wrong mimetype content/compression, duplicate
  member names, path traversal, disallowed compression, and every resource
  limit. Only member *position* (mimetype) and one specific missing
  *attribute* (version) are excused, each individually reported via
  `recovery_actions` -- nothing is silently repaired, and no semantic
  default (e.g. assuming "0.0.5") is invented for the missing version.
- A recovered file is a compatibility fixture, never treated as a
  spec-conformant baseline asset (its own vendored provenance file already
  makes this explicit; nothing in this test file or the product code
  changes that framing).
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from format_factory.ora import (
    OraArchiveError,
    OraValidationError,
    ReadMode,
    load,
    render_document,
)
from format_factory.ora.codec.stack_xml import UNSPECIFIED_VERSION

FIXTURES = Path(__file__).resolve().parents[1] / "ora" / "fixtures" / "third-party-gpl-mypaint"


# ── The 2 explicitly supported defects, tolerated only in TOLERANT mode ────


@pytest.mark.parametrize(
    ("fixture_name", "expected_first_member"),
    [("bigimage.ora", "data/"), ("fill_outlines.ora", "Thumbnails/")],
)
def test_mimetype_position_is_tolerated_only_in_tolerant_mode(
    fixture_name: str, expected_first_member: str
) -> None:
    path = FIXTURES / fixture_name
    with zipfile.ZipFile(path) as archive:
        assert archive.namelist()[0] == expected_first_member

    with pytest.raises(OraArchiveError, match="first"):
        load(path, mode=ReadMode.STRICT)

    image = load(path, mode=ReadMode.TOLERANT)
    assert any(
        "mimetype member was not the first archive member" in action
        for action in image.recovery_actions
    )
    # The mimetype member's own existence, compression, and exact content are
    # still mandatory in TOLERANT mode -- confirmed by construction here:
    # loading only succeeded because a genuinely-correct mimetype member
    # exists somewhere in the archive, per _check_mimetype's own logic.


def test_missing_version_attribute_is_tolerated_only_in_tolerant_mode() -> None:
    path = FIXTURES / "smallimage.ora"
    with zipfile.ZipFile(path) as archive:
        stack_xml = archive.read("stack.xml")
    assert b'version="' not in stack_xml

    with pytest.raises(OraValidationError, match="version"):
        load(path, mode=ReadMode.STRICT)

    image = load(path, mode=ReadMode.TOLERANT)
    assert any(
        "no 'version' attribute" in action for action in image.recovery_actions
    )
    # No semantic default was invented -- the document's own version is the
    # explicit sentinel, never a real OpenRaster version string.
    assert image.document.version == UNSPECIFIED_VERSION


# ── Narrow exception, not a general relaxation ──────────────────────────


def test_tolerant_mode_still_rejects_a_missing_w_attribute_unrelated_to_the_2_supported_defects() -> None:
    """The enumerated exception is `version` only -- `w`/`h` (or any other
    required attribute) missing must still raise in TOLERANT mode. Proves
    this is a narrow, named exception list, not "any missing attribute is
    now tolerated"."""
    payload = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image h="6" version="0.0.5"><stack><layer name="l" src="data/l.png"/></stack></image>'
    )
    archive_bytes = _minimal_archive(stack_xml=payload)

    with pytest.raises(OraValidationError, match="w"):
        load(archive_bytes, mode=ReadMode.TOLERANT)


def test_tolerant_mode_still_rejects_an_entirely_missing_mimetype_member() -> None:
    """The enumerated exception is mimetype *position* only -- a mimetype
    member that is entirely absent must still raise in TOLERANT mode."""
    archive_bytes = _minimal_archive(omit_mimetype=True)

    with pytest.raises(OraArchiveError, match="mimetype"):
        load(archive_bytes, mode=ReadMode.TOLERANT)


def test_tolerant_mode_still_rejects_wrong_mimetype_content() -> None:
    archive_bytes = _minimal_archive(mimetype_payload=b"image/png")

    with pytest.raises(OraArchiveError, match="mimetype"):
        load(archive_bytes, mode=ReadMode.TOLERANT)


def test_tolerant_mode_still_rejects_path_traversal() -> None:
    archive_bytes = _minimal_archive(extra_member=("../evil.txt", b"x"))

    with pytest.raises(OraArchiveError, match="traverses"):
        load(archive_bytes, mode=ReadMode.TOLERANT)


def test_tolerant_mode_still_rejects_duplicate_member_names() -> None:
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, b"image/openraster")
        archive.writestr(
            "stack.xml",
            b'<?xml version="1.0"?><image w="1" h="1" version="0.0.5">'
            b'<stack><layer name="l" src="data/l.png"/></stack></image>',
        )
        archive.writestr("data/l.png", b"x")
        archive.writestr("data/l.png", b"y")  # duplicate name

    with pytest.raises(OraArchiveError, match="duplicate"):
        load(buffer.getvalue(), mode=ReadMode.TOLERANT)


# ── Rendering reached after safe tolerant ingestion ─────────────────────


@pytest.mark.parametrize("fixture_name", ["bigimage.ora", "fill_outlines.ora", "smallimage.ora"])
def test_a_recovered_mypaint_fixture_renders_without_crashing(fixture_name: str) -> None:
    """Proves TOLERANT ingestion produces a genuinely usable document, not
    merely one that avoids raising -- render_document() runs to completion
    on real, independently-produced layer/group structure it was never
    tested against before. Does NOT claim pixel-exact independent-producer
    ground truth (see PROVENANCE.md and this fixture's own embedded assets
    -- fill_outlines.ora's mergedimage.png is 64x64, not full-canvas
    resolution, so it cannot serve as a full-frame comparison target)."""
    path = FIXTURES / fixture_name
    image = load(path, mode=ReadMode.TOLERANT)

    rendered = render_document(image.document, image.members)

    assert rendered.width == image.document.width
    assert rendered.height == image.document.height


def test_a_recovered_fixture_is_never_indistinguishable_from_a_conformant_one() -> None:
    """A recovered file stays a compatibility fixture, not a spec
    -conformant baseline asset: recovery_actions is the caller-visible,
    unerasable signal that something was excused."""
    path = FIXTURES / "smallimage.ora"
    image = load(path, mode=ReadMode.TOLERANT)

    assert len(image.recovery_actions) > 0


# ── Fixture builder for the narrow-exception tests above ───────────────


def _minimal_archive(
    *,
    stack_xml: bytes | None = None,
    omit_mimetype: bool = False,
    mimetype_payload: bytes = b"image/openraster",
    extra_member: tuple[str, str | bytes] | None = None,
) -> bytes:
    import io

    if stack_xml is None:
        stack_xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<image w="1" h="1" version="0.0.5"><stack>'
            b'<layer name="l" src="data/l.png"/></stack></image>'
        )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        if not omit_mimetype:
            info = zipfile.ZipInfo("mimetype")
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, mimetype_payload)
        archive.writestr("stack.xml", stack_xml)
        archive.writestr("data/l.png", b"x")
        if extra_member is not None:
            name, payload = extra_member
            archive.writestr(name, payload if isinstance(payload, bytes) else payload.encode())
    return buffer.getvalue()
