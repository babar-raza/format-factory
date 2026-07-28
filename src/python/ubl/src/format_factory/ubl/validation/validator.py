"""Structural validation for the stable UBL 2.3 chassis."""

from __future__ import annotations

from format_factory.core import Diagnostic, ResourceLimits, Severity, ValidationReport

from .._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ..model import UblDocument

_CBC_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
)
_SIGNATURE_LOCAL_NAMES = frozenset({"Signature", "UBLDocumentSignatures"})


def _local(qname: str) -> str:
    return qname.rsplit("}", 1)[-1]


def validate(
    value: UblDocument,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Validate supported root, QName, signature, and basic version invariants.

    This chassis validation is deliberately not an XSD-conformance claim.
    Full schema and cardinality validation remains a mandatory open obligation.
    """

    del limits
    diagnostics: list[Diagnostic] = []
    selected = profile or "UBL-2.3"
    if selected != "UBL-2.3":
        diagnostics.append(
            Diagnostic(
                "ubl.profile.unsupported",
                f"stable profile supports only UBL-2.3, got {selected!r}",
            )
        )
    if value.root_name not in ROOT_NAME_SET:
        diagnostics.append(
            Diagnostic(
                "ubl.root.unsupported",
                f"unsupported UBL document root {value.root_name!r}",
            )
        )
        return ValidationReport(diagnostics)
    expected_namespace = ROOT_NAMESPACES[value.root_name]
    if value.namespace != expected_namespace:
        diagnostics.append(
            Diagnostic(
                "ubl.root.namespace",
                f"{value.root_name} must use namespace {expected_namespace!r}",
            )
        )
    version_values = [
        node.text.strip()
        for node in value.root.children
        if node.qname == f"{{{_CBC_NAMESPACE}}}UBLVersionID"
    ]
    if len(version_values) > 1:
        diagnostics.append(
            Diagnostic(
                "ubl.version.duplicate",
                "document has more than one UBLVersionID",
            )
        )
    for version in version_values:
        if version != "2.3":
            diagnostics.append(
                Diagnostic(
                    "ubl.version.unsupported",
                    f"stable profile requires UBLVersionID 2.3, got {version!r}",
                )
            )
    signature_nodes = [
        node for node in value.root.iter() if _local(node.qname) in _SIGNATURE_LOCAL_NAMES
    ]
    if signature_nodes and not value.signature_preserved:
        diagnostics.append(
            Diagnostic(
                "ubl.signature.invalidated",
                "signed content has been edited or lacks its source digest",
                severity=Severity.WARNING,
            )
        )
    return ValidationReport(diagnostics)
