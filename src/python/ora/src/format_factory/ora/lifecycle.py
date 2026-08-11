"""ORA-LIFECYCLE-001, ORA-WRITE-001, ORA-BASELINEASSET-001 — load, validate, write.

This is what makes OpenRaster usable rather than merely inspectable: an archive
goes in, a document comes out, and the document goes back out as an archive the
loader accepts.

Two design choices carry most of the weight.

**Lossless by default.** A loaded image keeps its original members verbatim,
including the original `stack.xml` bytes. Writing re-emits them, so a vendor
extension this library does not model survives a round trip. Defaulting to
`CANONICAL` would silently discard those on any load-then-save, which is the
destructive option and the wrong default for a format whose stated goal is
"saving without destructive pixel operations".

**Determinism by construction.** Member order is fixed, timestamps are pinned to
the ZIP epoch, and compression is fixed, so an unchanged document serializes to
identical bytes every time and a re-written archive is a fixed point. Anything
derived from wall-clock time or dict ordering would break that silently.
"""

from __future__ import annotations

import io
import os
import re
import zipfile
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import IO, Union

from format_factory.core import (
    DEFAULT_LIMITS,
    Diagnostic,
    ResourceLimits,
    Severity,
    ValidationReport,
)

from .codec.assets import MERGED_IMAGE_MEMBER, THUMBNAIL_MEMBER
from .codec.container import MIMETYPE_MEMBER, OPENRASTER_MEDIA_TYPE, STACK_MEMBER, OraContainer
from .codec.png_metadata import read_png_metadata
from .codec.stack_xml import parse_stack
from .errors import OraError, OraLimitError, OraValidationError
from .model.document import DEFAULT_RESOLUTION_PPI, OraDocument
from .model.stack import DEFAULT_COMPOSITE_OP, OraLayer, OraStack, OraText
from .modes import ReadMode

#: The ZIP epoch. Every written member carries it, so output never depends on
#: when the write happened.
NORMALIZED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

BASELINE_VERSION = "0.0.2"


class PreservationMode(Enum):
    """LOSSLESS re-emits the original stack.xml; CANONICAL regenerates it."""

    LOSSLESS = "lossless"
    CANONICAL = "canonical"


Source = Union[bytes, bytearray, "os.PathLike[str]", str, IO[bytes]]


@dataclass(frozen=True)
class OraImage:
    """A loaded OpenRaster image: its model, its members, and how it was read."""

    document: OraDocument
    members: dict[str, bytes] = field(repr=False)
    declared_version: str = BASELINE_VERSION
    detected_version: str = BASELINE_VERSION
    recovery_actions: tuple[str, ...] = ()


def _read_source(source: Source) -> bytes:
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    if isinstance(source, (str, os.PathLike)):
        return Path(source).read_bytes()
    if hasattr(source, "read"):
        return source.read()
    raise TypeError(
        f"cannot load an OpenRaster image from {type(source).__name__}; expected "
        "bytes, a filesystem path, or a readable binary stream"
    )


def _detect_version(document: OraDocument, members: dict[str, bytes]) -> str:
    """Infer the profile the document actually uses, ignoring what it declares.

    A file may declare 0.0.1 and use 0.0.4 features, or declare 0.0.5 and use
    none. Reporting both separately lets a caller notice the disagreement; a
    single "version" would have to pick one and hide the other.
    """
    if _uses_isolation(document.root):
        return "0.0.4"  # isolation semantics
    if (document.xres, document.yres) != (DEFAULT_RESOLUTION_PPI, DEFAULT_RESOLUTION_PPI):
        return "0.0.3"  # xres/yres
    if MERGED_IMAGE_MEMBER in members:
        return "0.0.2"  # mergedimage.png became mandatory
    return "0.0.1"


def _uses_isolation(stack: OraStack) -> bool:
    for child in stack.children:
        if isinstance(child, OraStack):
            if child.isolation != "auto" or _uses_isolation(child):
                return True
        if child.opacity < 1.0 or child.composite_op != DEFAULT_COMPOSITE_OP:
            return True
    return False


_PROFILE_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _parse_profile_version(value: str) -> tuple[int, int, int] | None:
    """Parse a well-formed x.y.z profile version, or None if it isn't one.

    `version` is a required attribute with no format constraint in the
    specification's own grammar -- a document may declare anything. Drift
    can only be judged between two comparable values, so an unparseable
    declared version means "cannot determine", not "assume the worst".
    """
    match = _PROFILE_VERSION_PATTERN.match(value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _version_drift_diagnostics(declared_version: str, detected_version: str) -> list[Diagnostic]:
    """ORA-VALIDATE-001: "distinguish errors from interoperability warnings."

    A document that declares an older profile than the features it actually
    uses require is not invalid -- this reader still parses it correctly --
    but a strict reader honoring only the declared version may reject or
    misinterpret it. That is exactly an interoperability warning, not an
    error: reported at Severity.WARNING, which ValidationReport.is_valid
    deliberately does not count against validity.
    """
    declared = _parse_profile_version(declared_version)
    detected = _parse_profile_version(detected_version)
    if declared is None or detected is None or declared >= detected:
        return []
    return [
        Diagnostic(
            code="ORA_DECLARED_VERSION_BELOW_DETECTED",
            message=(
                f"document declares profile {declared_version} but uses "
                f"features that require profile {detected_version}; readers "
                "that enforce the declared version strictly may reject or "
                "misinterpret it"
            ),
            severity=Severity.WARNING,
        )
    ]


def _collect_layer_sources(node: OraStack | OraLayer | OraText) -> list[str]:
    """Walk the stack tree and return every layer src path."""
    sources: list[str] = []
    if isinstance(node, OraLayer) and node.src:
        sources.append(node.src)
    if isinstance(node, OraStack):
        for child in node.children:
            sources.extend(_collect_layer_sources(child))
    return sources


def _layer_png_diagnostics(
    document: OraDocument,
    members: dict[str, bytes],
    limits: ResourceLimits,
) -> list[Diagnostic]:
    """Validate that every layer src references a valid PNG member."""
    found: list[Diagnostic] = []
    for src in _collect_layer_sources(document.root):
        if src not in members:
            found.append(
                Diagnostic(
                    code="ORA_LAYER_SOURCE_MISSING",
                    message=f"layer references {src!r} which is not in the archive",
                    severity=Severity.ERROR,
                )
            )
            continue
        try:
            read_png_metadata(members[src], limits=limits)
        except (OraError, OraValidationError) as exc:
            found.append(
                Diagnostic(
                    code="ORA_LAYER_SOURCE_INVALID_PNG",
                    message=f"layer source {src!r} is not a valid PNG: {exc}",
                    severity=Severity.ERROR,
                )
            )
    return found


def _baseline_asset_diagnostics(members: dict[str, bytes]) -> list[Diagnostic]:
    """ORA-BASELINEASSET-001, expressed as findings rather than exceptions."""
    found: list[Diagnostic] = []

    thumbnail = members.get(THUMBNAIL_MEMBER)
    if thumbnail is None:
        found.append(
            Diagnostic(
                code="ORA_THUMBNAIL_MISSING",
                message=f"{THUMBNAIL_MEMBER} is required and is absent",
                severity=Severity.ERROR,
            )
        )
    else:
        try:
            metadata = read_png_metadata(thumbnail)
        except (OraError, OraValidationError) as exc:
            found.append(
                Diagnostic(
                    code="ORA_THUMBNAIL_UNREADABLE",
                    message=f"{THUMBNAIL_MEMBER} is not a readable PNG: {exc}",
                    severity=Severity.ERROR,
                )
            )
        else:
            if not metadata.satisfies_thumbnail_constraints():
                found.append(
                    Diagnostic(
                        code="ORA_THUMBNAIL_NON_CONFORMING",
                        message=(
                            f"{THUMBNAIL_MEMBER} must be a non-interlaced PNG with 8 "
                            f"bits per channel and at most 256x256, but is "
                            f"{metadata.width}x{metadata.height} at {metadata.bit_depth}-bit"
                            + (" interlaced" if metadata.interlaced else "")
                        ),
                        severity=Severity.ERROR,
                    )
                )

    merged = members.get(MERGED_IMAGE_MEMBER)
    if merged is None:
        found.append(
            Diagnostic(
                code="ORA_MERGED_IMAGE_MISSING",
                message=f"{MERGED_IMAGE_MEMBER} is mandatory since profile 0.0.2 and is absent",
                severity=Severity.ERROR,
            )
        )
    else:
        try:
            metadata = read_png_metadata(merged)
        except (OraError, OraValidationError) as exc:
            found.append(
                Diagnostic(
                    code="ORA_MERGED_IMAGE_UNREADABLE",
                    message=f"{MERGED_IMAGE_MEMBER} is not a readable PNG: {exc}",
                    severity=Severity.ERROR,
                )
            )
        else:
            if not metadata.satisfies_merged_image_constraints():
                found.append(
                    Diagnostic(
                        code="ORA_MERGED_IMAGE_NON_CONFORMING",
                        message=(
                            f"{MERGED_IMAGE_MEMBER} must carry 8 or 16 bits per channel, "
                            f"but declares {metadata.bit_depth}"
                        ),
                        severity=Severity.ERROR,
                    )
                )

    return found


def replace_baseline_asset(
    image: OraImage,
    *,
    thumbnail: bytes | None = None,
    merged_image: bytes | None = None,
) -> OraImage:
    """Return a copy of `image` with its thumbnail and/or merged-image
    member replaced by caller-supplied bytes, each validated against the
    exact same constraints `_baseline_asset_diagnostics` enforces on load.

    ORA-BASELINEASSET-001: "read, validate, generate, and replace required
    thumbnail and flattened-view assets." This package has no image
    -generation capability (no flattening/downscaling renderer exists) --
    "generate" remains genuinely unbuilt. "Replace" is the separable part:
    a caller who has already produced a new baseline asset by some other
    means (their own renderer, a different tool) can swap it in and have
    it validated the same way a freshly loaded document's own assets are,
    refused rather than silently accepted if it does not conform.
    """
    if thumbnail is None and merged_image is None:
        raise OraValidationError(
            "replace_baseline_asset requires at least one of thumbnail or "
            "merged_image"
        )

    members = dict(image.members)

    if thumbnail is not None:
        metadata = read_png_metadata(thumbnail)
        if not metadata.satisfies_thumbnail_constraints():
            raise OraValidationError(
                f"replacement {THUMBNAIL_MEMBER} must be a non-interlaced PNG "
                f"with 8 bits per channel and at most 256x256, but is "
                f"{metadata.width}x{metadata.height} at {metadata.bit_depth}-bit"
                + (" interlaced" if metadata.interlaced else "")
            )
        members[THUMBNAIL_MEMBER] = thumbnail

    if merged_image is not None:
        metadata = read_png_metadata(merged_image)
        if not metadata.satisfies_merged_image_constraints():
            raise OraValidationError(
                f"replacement {MERGED_IMAGE_MEMBER} must carry 8 or 16 bits "
                f"per channel, but declares {metadata.bit_depth}"
            )
        members[MERGED_IMAGE_MEMBER] = merged_image

    return replace(image, members=members)


def load(
    source: Source,
    *,
    mode: ReadMode = ReadMode.STRICT,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> OraImage:
    """Load an OpenRaster image from bytes, a path, or a readable stream."""
    payload = _read_source(source)
    container = OraContainer.from_bytes(payload, limits=limits, mode=mode)
    members = {name: container.read(name) for name in container.names}

    document = parse_stack(members[STACK_MEMBER], limits=limits, mode=mode)
    # What the file says about itself, kept verbatim and never rewritten.
    declared_version = document.version

    diagnostics = _baseline_asset_diagnostics(members)
    diagnostics.extend(_layer_png_diagnostics(document, members, limits))
    # Container- and stack.xml-level recoveries (mimetype position, missing
    # version) are already mode-gated inside from_bytes()/parse_stack()
    # themselves -- they raised already, in STRICT, before this line runs.
    recovery: list[str] = [*container.recovery_actions, *document.recovery_actions]
    if diagnostics:
        if mode is ReadMode.STRICT:
            raise OraValidationError(
                "; ".join(diagnostic.message for diagnostic in diagnostics)
            )
        # Tolerant: the layer tree is intact and readable, so the document is
        # usable. What was wrong is reported rather than repaired silently.
        recovery.extend(diagnostic.message for diagnostic in diagnostics)

    return OraImage(
        document=document,
        members=members,
        declared_version=declared_version,
        detected_version=_detect_version(document, members),
        recovery_actions=tuple(recovery),
    )


def loads(
    payload: bytes,
    *,
    mode: ReadMode = ReadMode.STRICT,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> OraImage:
    """Load an OpenRaster image from in-memory bytes; narrows `load`'s `Source`
    parameter (bytes, path, or stream) to bytes only, matching `dumps`'s own
    counterpart on the write side."""
    return load(payload, mode=mode, limits=limits)


def validate(source: Source, *, limits: ResourceLimits = DEFAULT_LIMITS) -> ValidationReport:
    """Validate without raising.

    A validator that raises on the worst input is not a validator: the caller
    asked for a report, and "this is not a ZIP" is a finding like any other.

    ``OraError``, ``OraValidationError``, and ``OraLimitError`` are three
    siblings (each descends directly from a different `format_factory.core`
    base -- `FormatParseError`, `FormatValidationError`, `ResourceLimitError`
    respectively), not a single hierarchy, so all three must be named
    explicitly here. Catching only `OraError` -- the mistake this replaced --
    let a malformed stack.xml (`parse_stack` raises `OraValidationError`) or
    an oversized/hostile payload (raises `OraLimitError`) crash this
    "never raises" validator instead of being reported.
    """
    try:
        payload = _read_source(source)
        container = OraContainer.from_bytes(payload, limits=limits)
        members = {name: container.read(name) for name in container.names}
        document = parse_stack(members[STACK_MEMBER], limits=limits)
    except (OraError, OraValidationError, OraLimitError) as exc:
        return ValidationReport(
            diagnostics=(
                Diagnostic(
                    code="ORA_UNREADABLE",
                    message=str(exc),
                    severity=Severity.FATAL,
                ),
            )
        )

    all_diagnostics = _baseline_asset_diagnostics(members)
    all_diagnostics.extend(_layer_png_diagnostics(document, members, limits))
    all_diagnostics.extend(
        _version_drift_diagnostics(document.version, _detect_version(document, members))
    )
    return ValidationReport(diagnostics=tuple(all_diagnostics))


def _canonical_stack_xml(document: OraDocument) -> bytes:
    """Regenerate stack.xml from the model, deterministically.

    Attributes are emitted in a fixed order and defaults are written explicitly,
    so the same model always produces the same bytes.
    """

    def render(node: OraStack | OraLayer | OraText, depth: int) -> list[str]:
        indent = "  " * depth
        attributes = []
        if node.name is not None:
            attributes.append(("name", node.name))
        attributes.append(("x", str(node.x)))
        attributes.append(("y", str(node.y)))
        attributes.append(("opacity", f"{node.opacity:g}"))
        attributes.append(("visibility", node.visibility))
        attributes.append(("composite-op", node.composite_op))
        if isinstance(node, OraStack):
            attributes.append(("isolation", node.isolation))
        if isinstance(node, (OraLayer, OraText)) and node.src:
            attributes.append(("src", node.src))

        rendered = " ".join(f'{key}="{_escape(value)}"' for key, value in attributes)
        tag = {OraStack: "stack", OraLayer: "layer", OraText: "text"}[type(node)]

        if isinstance(node, OraStack):
            lines = [f"{indent}<{tag} {rendered}>"]
            for child in node.children:
                lines.extend(render(child, depth + 1))
            lines.append(f"{indent}</{tag}>")
            return lines
        return [f"{indent}<{tag} {rendered}/>"]

    body = "\n".join(render(document.root, 1))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<image w="{document.width}" h="{document.height}" '
        f'version="{_escape(document.version)}" '
        f'xres="{document.xres}" yres="{document.yres}">\n'
        f"{body}\n"
        "</image>\n"
    ).encode("utf-8")


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def dumps(
    image: OraImage,
    *,
    preservation: PreservationMode = PreservationMode.LOSSLESS,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> bytes:
    """Serialize deterministically.

    The same image in the same mode always produces identical bytes: the
    mimetype sentinel first and STORED, remaining members in sorted order, every
    timestamp pinned to the ZIP epoch, and a fixed compression method. Nothing
    here consults the clock or relies on dict ordering.
    """
    members = dict(image.members)
    if preservation is PreservationMode.CANONICAL:
        members[STACK_MEMBER] = _canonical_stack_xml(image.document)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        sentinel = zipfile.ZipInfo(MIMETYPE_MEMBER, date_time=NORMALIZED_TIMESTAMP)
        sentinel.compress_type = zipfile.ZIP_STORED
        sentinel.external_attr = 0o644 << 16
        archive.writestr(sentinel, OPENRASTER_MEDIA_TYPE)

        for name in sorted(members):
            if name == MIMETYPE_MEMBER:
                continue
            info = zipfile.ZipInfo(name, date_time=NORMALIZED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, members[name])

    payload = buffer.getvalue()
    if len(payload) > limits.max_output_bytes:
        raise OraLimitError(
            f"serialized archive is {len(payload)} bytes, over the limit of "
            f"{limits.max_output_bytes}"
        )
    return payload


def dump(
    image: OraImage,
    destination: "os.PathLike[str] | str | IO[bytes]",
    *,
    preservation: PreservationMode = PreservationMode.LOSSLESS,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> None:
    """Write to a path or a writable binary stream."""
    payload = dumps(image, preservation=preservation, limits=limits)
    if isinstance(destination, (str, os.PathLike)):
        Path(destination).write_bytes(payload)
        return
    if not hasattr(destination, "write"):
        raise TypeError(
            f"cannot write an OpenRaster image to {type(destination).__name__}; "
            "expected a filesystem path or a writable binary stream"
        )
    destination.write(payload)


__all__ = [
    "BASELINE_VERSION",
    "NORMALIZED_TIMESTAMP",
    "OraImage",
    "PreservationMode",
    "ReadMode",
    "dump",
    "dumps",
    "load",
    "loads",
    "validate",
]
