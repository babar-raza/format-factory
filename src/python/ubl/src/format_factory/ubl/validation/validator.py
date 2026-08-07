"""Structural validation for the stable UBL 2.3 chassis."""

from __future__ import annotations

from format_factory.core import Diagnostic, ResourceLimits, Severity, ValidationReport

from .._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ..model import UblDocument

_CBC_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
)
_EXT_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
)
_UBL_EXTENSIONS_QNAME = f"{{{_EXT_NAMESPACE}}}UBLExtensions"
_UBL_EXTENSION_QNAME = f"{{{_EXT_NAMESPACE}}}UBLExtension"
_EXTENSION_CONTENT_QNAME = f"{{{_EXT_NAMESPACE}}}ExtensionContent"
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
    diagnostics.extend(_extension_diagnostics(value))
    return ValidationReport(diagnostics)


def _extension_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """ext:UBLExtensions must be the first optional component in sequence
    order; each ext:UBLExtension must contain exactly one ext:ExtensionContent,
    which must itself contain exactly one apex element."""

    diagnostics: list[Diagnostic] = []
    for index, node in enumerate(value.root.children):
        if node.qname != _UBL_EXTENSIONS_QNAME:
            continue
        if index != 0:
            diagnostics.append(
                Diagnostic(
                    "ubl.extensions.position",
                    "ext:UBLExtensions must be the first optional component "
                    "in the document sequence",
                )
            )
        for extension in node.children:
            if extension.qname != _UBL_EXTENSION_QNAME:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extensions.child",
                        "ext:UBLExtensions may only contain ext:UBLExtension "
                        f"children, found {extension.qname!r}",
                    )
                )
                continue
            content_children = [
                child for child in extension.children
                if child.qname == _EXTENSION_CONTENT_QNAME
            ]
            if len(content_children) != 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extension.content.cardinality",
                        "ext:UBLExtension must contain exactly one "
                        f"ext:ExtensionContent, found {len(content_children)}",
                    )
                )
                continue
            if len(content_children[0].children) != 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.extension.content.apex",
                        "ext:ExtensionContent must contain exactly one apex "
                        f"element, found {len(content_children[0].children)}",
                    )
                )
    return diagnostics
