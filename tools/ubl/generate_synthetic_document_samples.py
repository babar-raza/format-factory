"""Generate minimal, schema-valid synthetic UBL document instances.

UBL-WRITE-001 (SAL-UBL-OBL-F9D5251F2302AE3A): OASIS has never published an
example instance for 36 of UBL's 91 root document types, in any UBL version
(see reports/format-contract-layer/ubl-sample-coverage-research-memo.md).
That is a genuine gap in the available *real-world* corpus, but it does not
mean this package's own writer is untestable for those 36 types: they can be
tested against the pinned official OASIS schemas, deterministic synthetic
fixtures, and a round trip, without needing an official example at all.

This script walks each missing type's own vendored maindoc XSD
(src/python/ubl/src/format_factory/ubl/validation/schemas/maindoc/) using
the `xmlschema` library's real content-model introspection -- not a
hand-maintained per-type field list -- and builds the smallest tree that
satisfies every `minOccurs>=1` particle, recursively, with deterministic
placeholder leaf values chosen by primitive type (and by enumeration/pattern
facet when the schema restricts one). A `choice` group picks only its first
branch. `dumps()` (this package's own writer) reorders children into schema
sequence order regardless of the order this script builds them in, so this
script does not need to track schema ordering itself.

Every generated instance is labeled SYNTHETIC_SCHEMA_DERIVED in its own
manifest entry -- never presented as an OASIS example -- and is validated
against the same real official schema before being trusted as a fixture.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from typing import Any

import xmlschema

REPO_ROOT = Path(__file__).resolve().parents[2]
UBL_SRC = REPO_ROOT / "src" / "python" / "ubl" / "src"
MAINDOC_DIR = UBL_SRC / "format_factory" / "ubl" / "validation" / "schemas" / "maindoc"
OUTPUT_DIR = REPO_ROOT / "samples" / "by-format" / "ubl" / "synthetic"

sys.path.insert(0, str(UBL_SRC))

from format_factory.ubl import UblWriteError, dumps, loads  # noqa: E402
from format_factory.ubl.model.document import XmlNode  # noqa: E402
from format_factory.ubl.model.root_types import ROOT_CLASSES  # noqa: E402
from format_factory.ubl.validation.schema_validator import schema_validate  # noqa: E402

# The 36 root types with no official OASIS example in any UBL release,
# per ubl-sample-coverage-research-memo.md's own independently re-verified list.
MISSING_TYPES: tuple[str, ...] = (
    "ApplicationResponse", "AttachedDocument", "AwardedNotification", "BillOfLading",
    "CallForTenders", "Catalogue", "CatalogueDeletion", "CatalogueItemSpecificationUpdate",
    "CataloguePricingUpdate", "CatalogueRequest", "CertificateOfOrigin",
    "ContractAwardNotice", "ContractNotice", "DocumentStatus", "DocumentStatusRequest",
    "Enquiry", "EnquiryResponse", "ExpressionOfInterestResponse", "GuaranteeCertificate",
    "ItemInformationRequest", "PackingList", "QualificationApplicationRequest",
    "QualificationApplicationResponse", "SelfBilledInvoice", "Tender", "TenderContract",
    "TenderReceipt", "TenderStatus", "TenderStatusRequest", "TenderWithdrawal",
    "TendererQualification", "TendererQualificationResponse", "UnawardedNotification",
    "UnsubscribeFromProcedureRequest", "UnsubscribeFromProcedureResponse",
    "UtilityStatement",
)

_MAX_DEPTH = 40


class GenerationError(RuntimeError):
    pass


def _placeholder_for_primitive(primitive: str | None, counter: itertools.count) -> str:
    n = next(counter)
    table = {
        "string": f"SYNTH-{n}",
        "normalizedString": f"SYNTH-{n}",
        "token": f"SYNTH-{n}",
        "ID": f"SYNTH-{n}",
        "language": "en",
        "anyURI": f"urn:synthetic:test:{n}",
        "date": "2026-01-01",
        "dateTime": "2026-01-01T00:00:00",
        "time": "00:00:00",
        "gYear": "2026",
        "gYearMonth": "2026-01",
        "gMonthDay": "--01-01",
        "duration": "P1D",
        "boolean": "true",
        "decimal": "1",
        "integer": "1",
        "nonNegativeInteger": "1",
        "positiveInteger": "1",
        "double": "1",
        "float": "1",
        "base64Binary": "AA==",
        "hexBinary": "00",
    }
    return table.get(primitive or "string", f"SYNTH-{n}")


def _leaf_text(xsd_type: Any, counter: itertools.count) -> str:
    """Text content for a (possibly CCTS-wrapped) simple-content type,
    honoring an enumeration or pattern facet when the schema restricts one."""
    content = xsd_type.content if hasattr(xsd_type, "content") and xsd_type.content is not None else xsd_type
    enumeration = getattr(content, "enumeration", None)
    if enumeration:
        return str(enumeration[0])
    primitive = getattr(content, "primitive_type", None)
    primitive_name = primitive.local_name if primitive is not None else None
    patterns = getattr(content, "patterns", None)
    if patterns:
        # A pattern-restricted value this generic generator cannot safely
        # synthesize (e.g. a specific checksum/format) -- surface clearly
        # rather than emit a value likely to fail validation silently later.
        raise GenerationError(
            f"pattern-restricted simple type with no enumeration and no known-safe "
            f"generator: primitive={primitive_name!r} pattern={patterns!r}"
        )
    return _placeholder_for_primitive(primitive_name, counter)


def _required_attributes(xsd_type: Any, counter: itertools.count) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for name, attribute in getattr(xsd_type, "attributes", {}).items():
        if getattr(attribute, "use", None) != "required":
            continue
        local = name.rsplit("}", 1)[-1] if name and name.startswith("{") else name
        primitive = getattr(attribute.type, "primitive_type", None)
        primitive_name = primitive.local_name if primitive is not None else None
        enumeration = getattr(attribute.type, "enumeration", None)
        attrs[local] = str(enumeration[0]) if enumeration else _placeholder_for_primitive(primitive_name, counter)
    return attrs


def _build_element_node(xsd_element: Any, counter: itertools.count, depth: int) -> XmlNode:
    if depth > _MAX_DEPTH:
        raise GenerationError(f"max recursion depth exceeded at {xsd_element.name!r} -- likely a schema cycle")
    xsd_type = xsd_element.type
    if xsd_type.has_simple_content():
        text = _leaf_text(xsd_type, counter)
        attrs = _required_attributes(xsd_type, counter)
        return XmlNode.create(xsd_element.name, attributes=attrs, text=text)
    children = tuple(_walk_group(xsd_type.content, counter, depth + 1)) if xsd_type.content is not None else ()
    attrs = _required_attributes(xsd_type, counter)
    return XmlNode.create(xsd_element.name, attributes=attrs, children=children)


def _walk_group(group: Any, counter: itertools.count, depth: int) -> list[XmlNode]:
    if depth > _MAX_DEPTH:
        raise GenerationError("max recursion depth exceeded walking a content model group")
    nodes: list[XmlNode] = []
    model = getattr(group, "model", "sequence")
    particles = list(group)
    if model == "choice":
        # Pick only the first required-capable branch -- exactly one
        # alternative satisfies a choice; including more would violate it.
        candidates = [p for p in particles if getattr(p, "min_occurs", 1) >= 0]
        if not candidates:
            return nodes
        particles = candidates[:1]
        # A choice's own branch is included regardless of that branch's own
        # min_occurs (the CHOICE itself is what carries the occurrence
        # requirement here) -- fall through to the same per-particle logic
        # below with an effective min_occurs of 1 for the chosen branch.
        chosen = particles[0]
        if hasattr(chosen, "type"):
            nodes.append(_build_element_node(chosen, counter, depth + 1))
        else:
            nodes.extend(_walk_group(chosen, counter, depth + 1))
        return nodes
    for particle in particles:
        min_occurs = getattr(particle, "min_occurs", 0)
        if min_occurs < 1:
            continue
        if hasattr(particle, "type"):
            nodes.append(_build_element_node(particle, counter, depth + 1))
        else:
            nodes.extend(_walk_group(particle, counter, depth + 1))
    return nodes


def build_minimal_document(root_name: str) -> bytes:
    xsd_path = MAINDOC_DIR / f"UBL-{root_name}-2.3.xsd"
    if not xsd_path.is_file():
        raise GenerationError(f"no maindoc schema found for {root_name!r} at {xsd_path}")
    schema = xmlschema.XMLSchema(str(xsd_path))
    if root_name not in schema.elements:
        raise GenerationError(f"schema for {root_name!r} does not declare a root element of that name")
    xsd_element = schema.elements[root_name]
    counter = itertools.count(1)
    root_node = _build_element_node(xsd_element, counter, depth=0)

    document_cls = ROOT_CLASSES[root_name]
    document = document_cls(root=root_node)
    return dumps(document)


def generate_all(*, write: bool = True) -> dict[str, dict[str, Any]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    for root_name in MISSING_TYPES:
        entry: dict[str, Any] = {"root_name": root_name}
        try:
            raw = build_minimal_document(root_name)
        except (GenerationError, UblWriteError) as exc:
            entry["status"] = "generation_failed"
            entry["error"] = str(exc)
            results[root_name] = entry
            continue

        report = schema_validate(raw, root_name=root_name)
        if report.diagnostics:
            entry["status"] = "schema_invalid"
            entry["error"] = "; ".join(d.message for d in report.diagnostics[:5])
            results[root_name] = entry
            continue

        try:
            reloaded = loads(raw)
            round_tripped = dumps(reloaded)
        except UblWriteError as exc:
            entry["status"] = "roundtrip_failed"
            entry["error"] = str(exc)
            results[root_name] = entry
            continue

        entry["status"] = "ok"
        entry["bytes"] = len(raw)
        entry["roundtrip_bytes"] = len(round_tripped)
        if write:
            out_path = OUTPUT_DIR / f"{root_name}.xml"
            out_path.write_bytes(raw)
            entry["path"] = str(out_path.relative_to(REPO_ROOT)).replace("\\", "/")
        results[root_name] = entry
    return results


def main() -> int:
    results = generate_all(write=True)
    ok = [k for k, v in results.items() if v["status"] == "ok"]
    failed = {k: v for k, v in results.items() if v["status"] != "ok"}
    print(f"[ubl-synthetic] {len(ok)}/{len(results)} generated and schema-valid")
    for name, entry in failed.items():
        print(f"[ubl-synthetic] FAILED {name}: {entry['status']}: {entry.get('error')}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
