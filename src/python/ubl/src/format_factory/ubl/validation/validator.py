"""Structural validation for the stable UBL 2.3 chassis."""

from __future__ import annotations

from format_factory.core import Diagnostic, ResourceLimits, Severity, ValidationReport

from .._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ..model import UblDocument, XmlNode

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
    diagnostics.extend(_namespace_shadowing_diagnostics(value))
    return ValidationReport(diagnostics)


def _namespace(qname: str) -> str:
    return qname[1:].split("}", 1)[0] if qname.startswith("{") else ""


def _namespace_shadowing_diagnostics(value: UblDocument) -> list[Diagnostic]:
    """SAL-UBL-OBL-0996E6D7B91D544F: model/typed.py's find()/find_all() (the
    navigation primitives used throughout this package) match children by
    local name only, never checking the expanded namespace -- a spoofed
    element sharing a real element's local name but placed in a different,
    untrusted namespace could be returned instead of, or ahead of, the
    genuine one.

    Rewriting find()/find_all() to check an expected namespace per call
    would need auditing and updating roughly 78 call sites across
    typed.py/aggregates.py/charges.py/reference.py/document.py -- a
    cross-cutting change with real blast radius, deliberately out of
    scope here (see this obligation's own missing_behavior text). Instead
    this detects the one structural signature every such spoofing attempt
    must share: two or more same-local-name children, in different
    namespaces, under one parent. No conformant UBL document produces
    this shape -- every field name is namespace-scoped and siblings-unique
    within its own vocabulary (cbc:/cac:/the root's own namespace). This
    makes validate() the safety net: a spoofed sibling fails validation
    before any find()-derived value is trusted downstream, even though
    find() itself remains naively vulnerable if called directly without
    validating first.

    Deliberately does not recurse into ext:ExtensionContent -- that
    subtree is explicitly opaque vendor content this package never reads
    via find()/find_all() by field name, so applying this check inside it
    would be a false-positive risk, not a real protection.
    """
    diagnostics: list[Diagnostic] = []

    def walk(node: XmlNode) -> None:
        by_local_name: dict[str, set[str]] = {}
        for child in node.children:
            by_local_name.setdefault(_local(child.qname), set()).add(
                _namespace(child.qname)
            )
        for local, namespaces in sorted(by_local_name.items()):
            if len(namespaces) > 1:
                diagnostics.append(
                    Diagnostic(
                        "ubl.namespace.shadowed_element",
                        f"element {local!r} appears under {_local(node.qname)!r} "
                        f"in {len(namespaces)} different namespaces "
                        f"{sorted(namespaces)!r} -- this shape never occurs in a "
                        "conformant UBL document and may indicate a spoofed element",
                    )
                )
        for child in node.children:
            if child.qname != _EXTENSION_CONTENT_QNAME:
                walk(child)

    walk(value.root)
    return diagnostics


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
